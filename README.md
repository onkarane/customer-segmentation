# Starbucks: Customer Segmentation Using Python

## 1. Introduction

Customer segmentation is the process of dividing customers into groups based on common characteristics so companies can market to each group effectively and appropriately. In order to demonstrate customer segmentation I will be doing "Cluster Analysis" to classify Starbucks customers into 3 distinct clusters.

## 2. Aim

Target Starbucks Customers for marketing campaign based on the offers received/viewed/completed by the customers along with the transaction details such as amount spent & amount rewarded back.

## 3. Dataset

The customer transaction data is provided by Starbucks and is a part of Udacity Data Science Nanodegree project. The dataset contains transaction data for 30 days.

The dataset contains three files:

1. portfolio.json: contains information about each offer & various attributes related to the offer
2. profile.json: contains metadata about customers
3. transcript.json: contains data related to event such as offer received/viewed/completed by a customer

## 4. Data Cleansing & Wrangling

Some highlights of the cleaning and transformation tasks include:

1. Identifying and labeling repeated offers uniquely.
2. Removing the misattribute offers Ex: offers viewed before even receiving.
3. Imputing null values.
4. Calculating Response Rate & Conversion Rate

Further details about about cleansing & data wrangling tasks can be found in [Cleansing_and_Wrangling](Cleansing_and_Wrangling.ipnyb) notebook.

## 5. Modeling

The following tasks were carried out for modeling:

1. Feature Scaling using Standard Scaler from Scikit-learn library.
2. Dimensionality reduction using Principle Component Analysis (PCA).
3. Clustering using K-Means algorithm.

## 6. Results

### Segment 1: Bogo Group

* Majority of the customers in this group are Females followed by the Other Category.
* As the name of the group suggests, this group mainly receives/views/completes the BOGO offers. As a result, they have higher bogo rewards awarded to them.
* In addtion, this group also has the highest income of all three segments, as well as total amount spent by them in transactions is also the highest.
* Finally, majority of the customers from this group became members from the year 2015 to 2017.

### Segment 2: Passive Group

* Majority of the customers in this group are Male and recevie highest number of informational offers.
* Altough, they have a decent view rate for both BOGO & DISCOUNT offers, the hardly ever opt in and complete the transactions using these offers.
* They also have the lowest income of all three groups, and most of them became members in the past couple of years i.e 2017 & 2018.

### Segment 3: Discount Group

* Majority of the customers in this group belong to the Other Category, followed by Female customers.
* This group receives/views/completes highest number of DISCOUNT offers. As a result, they have higher discount rewards awarded to them. In addition, this group also receives highest number of informational offers.
* The transactions completed by this group is the highest as compared to rest of the groups.
* Finally, these people have been the customers of starbucks consistently since 2013.

The analysis & output can be found in [Modeling](Modeling.ipynb) notebook.

