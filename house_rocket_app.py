
# ------------------------------
# how to run streamlit
# ------------------------------
# streamlit run <filename>.py


# Libraries
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import geopandas

#
# settings
st.set_page_config(
    layout="wide",
    initial_sidebar_state="auto",
)

#
# Helper Functions


@ st.cache(allow_output_mutation=True)
def get_data(path):

    data = pd.read_csv(path)
    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')

    return data


@st.cache(allow_output_mutation=True)
def get_geofile(url):
    geofile = geopandas.read_file(url)

    return geofile


def clean_data(data):
    # remove duplicates
    data = data.sort_values('id', ascending=False).drop_duplicates(
        subset='id', keep='first')

    # replace 33-bedrooms data with median value
    data.loc[data['bedrooms'] == 33, 'bedrooms'] = data['bedrooms'].median()

    return data


def set_feature(data):
    # add new features

    # ---------------------
    # add feature buy_house
    # indicates whether the house should be purchased or not
    # ---------------------

    # Good houses:
    # - floors < 3
    # - grades >= 7
    # - 0-2000 sqft of living space: 1-2 bedrooms and 1-2 bathrooms
    # - 2.000-5.0000 sqft of living space: 3-5 bedrooms | 3-5 bathrooms
    # - more than 5.0000 sqft of living space: at least 6 bedrooms and 6 bathrooms

    data['living_size'] = data['sqft_living'].apply(
        lambda x: 'small' if x <= 2000 else 'medium' if x <= 5000 else 'large')
    data['num_bedroom'] = data['bedrooms'].apply(
        lambda x: 'small' if x <= 2 else 'medium' if x <= 5 else 'large')
    data['num_bathroom'] = data['bathrooms'].apply(
        lambda x: 'small' if x <= 2 else 'medium' if x <= 5 else 'large')

    data['buy_house'] = 'No'
    data['buy_house'] = np.where((data['living_size'] == data['num_bedroom']) &
                                 (data['living_size'] == data['num_bathroom']) &
                                 (data['floors'] < 3) &
                                 (data['grade'] >= 7), "Yes", "No")

    # ---------------------
    # add feature price_sale
    # value the house should be sold
    # ---------------------

    # As we saw that location also impacts the price. Let's group the houses by zipcode and size living and calculate the average price
    # - If purchase price is higher than region median price + living size price, sales price will be equal to the price purchase + 10%
    # - If purchase price is lower than region median price + living size price, sales price will be equal to the price purchase + 30%

    # median price per region and living room size
    data_med_price = data.groupby(['zipcode', 'living_size'])[
        'price'].median().reset_index()
    data_med_price.rename(
        columns={'price': 'price_med_region_size'}, inplace=True)

    # merge
    data = pd.merge(data, data_med_price, how='inner',
                    on=['zipcode', 'living_size'])

    # value the house should be sold
    data['price_sale'] = 0
    data['price_sale'] = np.where((data['buy_house'] == "Yes") & (
        data['price'] <= data['price_med_region_size']), data['price']*1.1, data['price']*1.3)

    # ---------------------
    # add feature profit
    # profit made from the purchase and sale of the house
    # ---------------------
    data['profit'] = 0
    data['profit'] = np.where(data['buy_house'] == "Yes",
                              data['price_sale'] - data['price'], 0)

    return data


def intro(imgpath):

    # header
    st.title('Welcome to House Rocket Data Analysis')

    st.write("""
        ### House Rocket is a digital platform whose business model is to buy and sell real estate using technology
    """)

    st.write("""
        - This is not a real case
        - This dataset contains house sold between May 2014 and May 2015 for King County, which includes Seattle (USA). It is available on kaggle and can be downloaded from this [link](https://www.kaggle.com/harlfoxem/housesalesprediction)
        - Use the parameters in the left panel to filter the data
        """)

    st.image(imgpath,
             use_column_width=True)

    st.write("""
        #### Their main strategy is to buy good homes in great locations at low prices and then resell them later at higher prices. The greater the difference between buying and selling, the greater the companys profit and therefore the greater its revenue. However, homes have many attributes that make them more or less attractive to buyers and sellers, and location and time of year can also influence prices.
        """)

    st.write('---')

    return None


def slicers(data):

    st.sidebar.header("Houses Features")

    # filters option
    f_zipcode = st.sidebar.multiselect('Zipcode', data['zipcode'].unique())
    f_bedrooms = st.sidebar.multiselect('# of Bedrooms', sorted(
        set(data['bedrooms'].astype(int).unique())))
    f_bathrooms = st.sidebar.multiselect('# of Bathrooms', sorted(
        set(data['bathrooms'].astype(int).unique())))
    f_floors = st.sidebar.multiselect('# of Floors', sorted(
        set(data['floors'].astype(int).unique())))
    f_grade = st.sidebar.multiselect('Grade', sorted(
        set(data['grade'].astype(int).unique())))

    min_liv = int(data['sqft_living'].min())
    max_liv = int(data['sqft_living'].max())

    f_sqft_living = st.sidebar.slider(
        'Living Size (sqft)', min_value=min_liv, max_value=max_liv, value=max_liv)

    min_abv = int(data['sqft_above'].min())
    max_abv = int(data['sqft_above'].max())
    f_sqft_above = st.sidebar.slider(
        'Interior Size Above Basement (sqft)', min_value=min_abv, max_value=max_abv, value=max_abv)

    # filter dataset by parameters selected
    cat_filters = [[f_zipcode, 'zipcode'], [f_bedrooms, 'bedrooms'], [
        f_bathrooms, 'bathrooms'], [f_floors, 'floors'], [f_grade, 'grade']]

    num_filters = [[f_sqft_living, 'sqft_living'],
                   [f_sqft_above, 'sqft_above']]

    for filter in cat_filters:
        data = (data[data[filter[1]].isin(filter[0])]
                if filter[0] != [] else data)

    for filter in num_filters:
        data = data.loc[data[filter[1]] < filter[0]]

    return data


def maps(data, geofile):

    # -------------------
    # map showing houses to buy
    # -------------------

    # laying out the top section of the app
    row1_1, row1_2, row1_3 = st.columns((1, 3, 3))

    with row1_1:
        st.header('What houses that House Rocket should buy?')

        st.write(
            """
            #### A total of 21,436 homes were analyzed, but only 41% (8,889) are recommended for purchase. 
            #### The maps on the right side show where the best opportunities are among all the houses analyzed.
        """)

        st.header('After buying the house, how much should it be sold for?')

        st.write(
            """
            #### On the second map, click on the desired house to view for what price it should be sold and its features.
        """)

    #
    #

    with row1_2:

        st.subheader("Houses that House Rocket should buy or not")

        if data.empty:
            pass
        else:
            fig = px.scatter_mapbox(data,
                                    lat="lat",
                                    lon="long",
                                    color='buy_house',
                                    color_discrete_map={
                                        'Yes': 'blue', 'No': 'red'},
                                    center={"lat": data['lat'].mean(),
                                            "lon": data['long'].mean()},
                                    hover_name='id',
                                    hover_data={'zipcode': True,
                                                'profit': True,
                                                'price_sale': True,
                                                'price': True,
                                                'bedrooms': True,
                                                'bathrooms': True,
                                                'sqft_living': True,
                                                'sqft_above': True,
                                                'grade': True,
                                                'floors': True,
                                                'buy_house': False,
                                                'lat': False,
                                                'long': False},
                                    zoom=9
                                    )

            fig.update_layout(mapbox_style="carto-positron")
            fig.update_layout(height=600, margin={
                              "r": 0, "t": 0, "l": 0, "b": 0})

            # plot map
            st.plotly_chart(fig, use_container_width=True)

    #
    #

    with row1_3:

        # filter just the houses that should be bought
        df = data[data['buy_house'] == 'Yes']

        st.subheader("Recommended houses to buy clusted by region")

        if df.empty:
            pass
        else:
            # Map with Folium (empty base map)
            density_map = folium.Map(location=[df['lat'].mean(),
                                               df['long'].mean()],
                                     tiles="cartodbpositron",
                                     default_zoom_start=15)

            # insert point in map
            marker_cluster = MarkerCluster().add_to(density_map)

            # marker features
            for name, row in df.iterrows():
                folium.Marker([row['lat'], row['long']],
                              icon=folium.Icon(
                    color='red', icon="info-sign"),
                    tooltip='Click here to see popup',
                    size=row['profit'],
                    popup='House ID: {0}, Must be sold by: ${1}, Sold for ${2} on: {3}. Features: {4} sqft Living Interior, {5} sqft Above Interior, {6} Bedrooms, {7} Bathrooms, {8} Floors'
                    .format(row['id'],
                            row['price_sale'],
                            row['price'],
                            row['date'],
                            row['sqft_living'],
                            row['sqft_above'],
                            row['bedrooms'],
                            row['bathrooms'],
                            row['floors'])).add_to(marker_cluster)

            # plot map
            folium_static(density_map, width=1000, height=600)

    #
    #
    #

    row1_1, row1_2, row1_3 = st.columns((1, 3, 3))

    with row1_1:
        st.header('Where are the best opportunities?')

        st.write(
            """
            #### Maps on the right side are only considering the houses recommended for purchase.
            #### 98039, 98004 and 98112 zip codes represents the most promising regions, where are located the houses that will return the highest profit.
        """)

    with row1_2:

        # group profit by region (zipcode)
        df = df[['profit', 'zipcode']].groupby('zipcode').mean().reset_index()
        # rename columns to the same name of geofile dataframe
        df.columns = ['ZIP', 'PROFIT']

        geofile = pd.merge(geofile, df, how='inner', on=['ZIP'])
        geofile['PROFIT'] = geofile['PROFIT'].map('${:,.0f}'.format)

        st.subheader("Average expected profit per region")

        if df.empty:
            pass
        else:
            region_price_map = folium.Map(location=[data['lat'].mean(),
                                                    data['long'].mean()],
                                          tiles="cartodbpositron",
                                          default_zoom_start=8)

            region_price_map.choropleth(data=df,
                                        geo_data=geofile,
                                        columns=['ZIP', 'PROFIT'],
                                        key_on='feature.properties.ZIP',
                                        fill_color='YlOrRd',
                                        fill_opacity=1,
                                        line_opacity=0.2,
                                        legend_name='Average Profit')

            def style_function(x): return {'fillColor': '#ffffff',
                                           'color': '#000000',
                                           'fillOpacity': 0.1,
                                           'weight': 0.1}

            def highlight_function(x): return {'fillColor': '#000000',
                                               'color': '#000000',
                                               'fillOpacity': 0.50,
                                               'weight': 0.1}

            NIL = folium.features.GeoJson(
                geofile,
                style_function=style_function,
                control=False,
                highlight_function=highlight_function,
                tooltip=folium.features.GeoJsonTooltip(
                    fields=['ZIP', 'PROFIT'],
                    aliases=['Zipcode: ', 'Average Profit($): '],
                    style=(
                        "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                )
            )

            region_price_map.add_child(NIL)
            region_price_map.keep_in_front(NIL)
            folium.LayerControl().add_to(region_price_map)

            # plot map
            folium_static(region_price_map, width=1000, height=600)

    #
    #

    with row1_3:

        # filter just the houses that should be bought
        df = data[data['buy_house'] == 'Yes']

        st.subheader('Houses that House Rocket should buy per expected profit')

        if df.empty:
            pass
        else:
            fig = px.scatter_mapbox(df,
                                    lat="lat",
                                    lon="long",
                                    color='profit',
                                    size='profit',
                                    # color_continuous_scale=px.colors.sequential.Reds,
                                    center={"lat": data['lat'].mean(),
                                            "lon": data['long'].mean()},
                                    hover_name='id',
                                    hover_data={'zipcode': True,
                                                'profit': True,
                                                'price_sale': True,
                                                'price': True,
                                                'bedrooms': True,
                                                'bathrooms': True,
                                                'sqft_living': True,
                                                'sqft_above': True,
                                                'grade': True,
                                                'floors': True,
                                                'buy_house': False,
                                                'lat': False,
                                                'long': False},
                                    zoom=9
                                    )

            fig.update_layout(mapbox_style="carto-positron")
            fig.update_layout(height=600, margin={
                              "r": 0, "t": 0, "l": 0, "b": 0})

            # plot map
            st.plotly_chart(fig, use_container_width=True)

    return None


if __name__ == '__main__':

    # ETL

    # Parameters
    filepath = 'dataset/kc_house_data.csv'
    imgpath = 'image/image_house_rocket.jpg'
    url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'
    intro(imgpath)

    # Data extraction
    data = get_data(path=filepath)
    geofile = get_geofile(url)

    # Transformation
    data = clean_data(data)
    data = set_feature(data)

    # Loading
    data = slicers(data)
    maps(data, geofile)
