# House Rocket Data Analysis
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://lz-house-rocket-app.herokuapp.com/)

House Rocket is a digital platform whose business model is to buy and sell real estate using technology

![](image/image_house_rocket.jpg)

# 1. Business Problem

House Rocket main strategy is to buy good homes in great locations at low prices and then resell them later at higher prices. The greater the difference between buying and selling, the greater the companys profit and therefore the greater its revenue.

However, homes have many attributes that make them more or less attractive to buyers and sellers, and location and time of year can also influence prices.
The business team cannot make good purchasing decisions without analyzing the data and the portfolio is very large and takes a long time to analyze manually.

The main objective of this project is to find the best property purchase opportunities in the House Rocket portfolio. For this, 2 questions must be answered:
- **Which houses should House Rocket buy and at what purchase price?**
- **Once the house is purchased, what would the sale price be?**

# 2. Dataset Analysed

<em>This is not a real case: the dataset used contains house sold between May 2014 and May 2015 for King County, which includes Seattle (USA). 
It is available on kaggle and can be downloaded from this [link](https://www.kaggle.com/harlfoxem/housesalesprediction).</em>

- id - Unique ID for each home sold
- date - Date of the home sale
- price - Price of each home sold
- bedrooms - Number of bedrooms
- bathrooms - Number of bathrooms, where 0.5 accounts for a room with a toilet but no shower
- sqft_living - Square footage of the apartments interior living space
- sqft_lot - Square footage of the land space
- floors - Number of floors
- waterfront - A dummy variable for whether the apartment was overlooking the waterfront or not
- view - An index from 0 to 4 of how good the view of the property was
- condition - An index from 1 to 5 on the condition of the apartment,
- grade - An index from 1 to 13, where 1-3 falls short of building construction and design, 7 has an average level of construction and design, and 11-13 have a high quality level of construction and design.
- sqft_above - The square footage of the interior housing space that is above ground level
- sqft_basement - The square footage of the interior housing space that is below ground level
- yr_built - The year the house was initially built
- yr_renovated - The year of the house’s last renovation
- zipcode - What zipcode area the house is in
- lat - Lattitude
- long - Longitude
- sqft_living15 - The square footage of interior housing living space for the nearest 15 neighbors
- sqft_lot15 - The square footage of the land lots of the nearest 15 neighbors

# 3. Business Assumptions

The assumptions about the business problem is as follows:

- Houses`s price did not suffer inflation
- No tax fee was considered on the purchase amount
- No house has undergone any type of renovation that causes an appreciation

# 4. Solution Strategy

My strategy to solve this challenge was:

**Step 01. Data Extraction:** Load dataset and make an overview.

**Step 02. Data Transformation:** My goal is to identify nulls and data outside the scope of the business.

**Step 03. Add New Features:** Derive new attributes based on the original variables to better describe the phenomenon that will be modeled.

**Step 04. Exploratory Data Analysis:** Explore the data to find insights and better understand the impact of variables on houses price.

**Step 05. Answer Questions:** Identify the most significant attributes for answer business questions.

**Step 06. Data Visualization:** Create a dashboard using Streamlit to show the insights and results found.

**Step 07. Deploy Dashboard to Production:** Publish the dashboard in a cloud environment (Heroku) so that other people or services can use the results to improve the business decision.

# 5. Top 5 Data Insights

<ol>
  <li>Small houses with many bedrooms and/or bathrooms, loses purchase value</li>
  
  <li>Houses must have at least one bathroom to add value</li>
  
  <li>The higher the square footage, the higher the grade</li>
  
  <li>Small houses must have at least grade equals to 7</li>
  
  <li>Houses with a grade equals to 11 or more are above average</li>
</ol>


# 6. Business Results

#### Which houses should House Rocket buy?

Recommended houses for purchase have the following requirements:
- floors < 3
- grades >= 7
- 0-2000 sqft of living space: 1-2 bedrooms and 1-2 bathrooms 
- 2.000-5.0000 sqft of living space: 3-5 bedrooms | 3-5 bathrooms 
- more than 5.0000 sqft of living space: at least 6 bedrooms and 6 bathrooms

A total of 21,436 homes were analyzed, but only 8,889 are recommended for purchase, which represents a share of 41%.

| Houses Classification | # of Houses    | % of Houses  |
|:--------------------  |:---------------|:-------------|
| Buy                   | 8.889          | 41%          | 
| Not to buy            | 12.547         | 59%          |

#### Once the house is purchased, what would the sale price be?

Since the house`s location also impacts its price, I grouped the houses by zipcode and size living and calculate the average price:
- If purchase price is higher than region median price + living size price, sales price will be equal to the price purchase + 10%
- If purchase price is lower than region median price + living size price, sales price will be equal to the price purchase + 30%

As we are not considering the houses price`s inflation and that no house has been renovated over time, the price considered for the last purchase of the same is the price considered for the last purchase that was sold at the time.

| Sales Price Formula   | Sale Price      | Purchase Price  |Total Profit    |# of Houses     |Average Profit  |
|:--------------------  |:--------------- |:--------------- |:---------------|:---------------|:---------------|
| price purchase + 10%  | $2.344.796.449  | $2.131.633.135  | $213.163.314   | 4.242          | $50.251        |
| price purchase + 30%  | $4.983.222.841  | $3.833.248.339  | $1.149.974.502 | 4.647          | $247.466       |

The 8.889 houses recommended for purchase represent a total profit of $1,363,137,816.

#### Where are the best opportunities?

I order to identify the best opportunities, I calculated the average profit, grouping homes by region. Below we have a table with top 10 average profit by region:

|Zipcode |	Average Profit  |
|:------ |:---------------- |
|98039	 |$449.385          |
|98004	 |$358.378          |
|98112	 |$299.498          |
|98040	 |$290.464          |
|98102	 |$281.638          |
|98105	 |$253.246          |
|98199	 |$236.536          |
|98033	 |$234.179          |
|98109	 |$221.700          |
|98005	 |$212.597          |

98039, 98004 and 98112 zip codes represents the most promising regions, where are located the houses that will return the highest average profit.

Whereas, the investment in the first region (postal code 98039) will result in the same profit with the purchase and sale of a much smaller number of houses (less than half) in relation to the other regions.

**For this reason, House Rocket should start its investments by houses from 98039 zip code.** 

# 7. Conclusions
  
At the end of this project it was possible to identify the best opportunities in order to maximize the profit resulting from the purchase and sale of real estate in the King County area. 
The company has access to information on which properties to buy or not, the amount invested in the purchase, for what value the property should be sold and what the profit will be, qnd can easily identify which investments will bring you the greatest return. 

# 8. Next Steps
  
The next step is to analyze which properties should be renovated to increase the sale value. And what is the increase in the price given by each type of reform.

# 9. References
  
**1.** House Sales in King County, USA. Kaggle. Available in: https://www.kaggle.com/harlfoxem/housesalesprediction

**2.** Blog "Seja Um Data Scientist". Available in: https://sejaumdatascientist.com/os-5-projetos-de-data-science-que-fara-o-recrutador-olhar-para-voce/

**3.** Comunidade DS. Available in: https://www.comunidadedatascience.com/

