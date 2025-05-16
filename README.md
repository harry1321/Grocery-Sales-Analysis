# Cloud-Based Grocery Sales Analytics Pipeline

![Python](https://img.shields.io/badge/Python-3776ab?style=flat&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/-SQL-e69138?style=flat&logo=sql&logoColor=white)
![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?logo=apacheairflow&logoColor=white&style=flat)
![GCP](https://img.shields.io/badge/Google%20Cloud-4285F4?logo=googlecloud&logoColor=white&style=flat)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?logo=apachespark&logoColor=fff&style=flat)
![Livy](https://img.shields.io/badge/Apache%20Livy-Spark%20Job%20API-003B57?logo=apache&logoColor=white&style=flat)
![DBT](https://img.shields.io/badge/dbt-Data%20Modeling-F26639?logo=dbt&logoColor=white&style=flat)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?logo=terraform&logoColor=white&style=flat)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=FFFFFF)

---

<div align="center">

[Problem Statement](#problem-statement) •
[Solution](#solution-overview) •
[Project Details](#project-details) • 
[Running the Project](#how-to-run-this-project) <br>
[Dashboard](#dashboard) • 
[Contact](#contact-information) • 
[Acknowledgments](#acknowledgments)
</div>

---
This project demonstrates deploying an end to end data pipeline on cloud that transforms raw grocery sales data into actionable business insights. Using GCP, Spark, Airflow, DBT, and Looker Studio, the project automate data ingestion, transformation, and visualization to answer critical business questions such as:

- Who are our top-performing salespeople and customers?
- Which regions generate the most revenue?
- How do product categories contribute to revenue?
- What are our hot selling products?

By focusing on these metrics, the project emulates the day-to-day work of a data engineer supporting data analyst for decision-makering in sales and marketing.

<!-- This project builds a data engineering pipeline to analyze grocery sales data and produce an interactive dashboard. The dashboard enables us to explore revenue by cities, assess customer purchasing patterns, and evaluate salesperson performance to uncover key drivers behind sales trends. -->

## Problem Statement

<!-- This dashboard aims to tackle real-world business challenges such as understanding customer purchasing patterns, evaluating sales team effectiveness, and identifying high-performing regions. Specifically, the goal is to enable data-driven decisions that optimize marketing strategies, improve customer retention, and allocate sales resources more effectively.

The problem statement focuses on three core areas:
- Customer Purchase Behavior — Who are our repeat customers, and how much do they spend? What kind of product creates most revenue and what is the porpotion of each product category?
- Salesperson Effectiveness — Which employees are driving the most value?
- Geographic Sales Insights — Where are the sales hotspots across cities? -->

Transaction records come in every day, and retailers must make data-driven decisions to effectively manage their business. Without tools that automatically process this raw data, these records would be nothing more than meaningless numbers. Retailers could struggle with fragmented data and a lack of automated processing. Therefore, a scalable, scheduled data processing pipeline is essential.

Once the records are cleaned and organized, retailers can extract key business insights such as:

- Customer Behavior: Who are our repeat customers? What is their spending pattern?
- Sales Team Performance: Which employees generate the most revenue?
- Geographic Analysis: Which cities are leading in sales?

## Solution Overview
To address those problems, this project implemented a scalable ELT pipeline that will:

- Ingestes and processes over 6.7 million transaction records automatically using Airflow
- Generates product recommendations for customers using Spark
- Uses DBT to model and transform data into fact and dimension tables
- Visualizes data on Looker Studio

In the end of this ELT pipeline, a dashboard will be built to provide some business insights such as:
- Top 10 customers by order value
- Top 10 employees by sales
- Top 10 cities by revenue
- Hot selling products
- Revenue trends over time
- Revenue produce by product Category
- Customer segmentation by average order value

## Project Details
The data pipeline automates the data processing workflow utilizing the following tech stacks:
- [`Apache Airflow`](https://airflow.apache.org/) for data pipeline orchestration
- [`Google Cloud Platform (GCP)`](https://cloud.google.com/) services for data lake, data warehouse and virtual machine
- [`Apache Spark`](https://spark.apache.org/) for data processing
- [`Apache Livy`](https://livy.apache.org/) for using REST API ti trigger Spark jobs
- [`DBT`](https://www.getdbt.com/) for data modeling and transformation
- [`GitHub Actions`](https://github.com/features/actions) for CI/CD
- [`Terraform`](https://github.com/hashicorp/terraform) for cloud resources provision
- [`Looker Studio`](https://lookerstudio.google.com/) for building dashboard

### Data Pipeline Architecture

This pipeline contains the following parts of precessing data, and **all tasks are build and run on the cloud**:

- **Data Extraction**: In Airflow a task called get will download data files from [Kaggle Grocery Sales Database](https://www.kaggle.com/datasets/andrexibiza/grocery-sales-dataset) by KaggleAPI. 
    - This dataset is consists of sales transactions, customer demographics, product details, employee records, and geographical information across multiple cities. 
    - The Grocery Sales Dataset, sourced from Kaggle, comprises seven interconnected tables covering transactional, customer, product, and geographic data. 
    - The dataset includes detailed records of product categories, customers’ personal and location information, product attributes, employee details, and a comprehensive sales log. 
    - The data spans a four-month time period begins from January 1st in 2018 to May 10th in 2018 with 6,758,125 rows of transation data.

- **Data Loading**: In the second stage, the Airflow tasks stored the raw data in Google Cloud Storage for long term storage, and then loaded those files to BigQuery for further transformed and processed.

- **Data Processing & Transform**: In this stage, Airflow automatically used DBT for data transformation and PySpark for customer segmentation and generating product recommendations. 
    - In DBT models, seeds data firstly be created as tables, and then join raw data sperately to create customer, employee and product dimensional models.
    - After building dimensional tables, DBT builds a fact table called `fct_sales` **partioned by `SalesDay` and clustering by `CustomerID`**. The reason for doing so is that the downstream models will group by `CustomerID` frequently and the dashboard will apply a date range filter to filter out target data.
    - Spark is used to categorize customers based on RFM model and generate recommendations for each customer with ALS model. In this stage, two fact tables is created.
    - In the gold layer of data, four models are created in order to build the KPI dashboard, which are `mart_sales_summary`, `mart_customer_behavior`,  `mart_employee_performance` and `mart_recommend`.

- **CI/CD**: To achieve continous deployment without manual intervention, GitHub Actions is used to detect commits or change in DAGs and cloud resources. If commits are pushed in main branch, compute engines working on cloud will automactically catch up the latest version pipelines.

Diagram below shows an overview of data pipeline architecture used in this project.

<p align="center">
    <img src="/assets/architecture.png" width="60%", height="60%"
    <em></em>
</p>

## How to Run This Project

If you would like to learn more about this project, please follow the instructions in [`reproduce.md`](/reproduce.md).

## Dashboard
You can access this dashboard from [here](https://lookerstudio.google.com/s/jEFS_2hqVB0).

![dashboard.png](/assets/dashboard_snap.png)

## Contact Information

Feel free to reach out!

📧 Email: [r08521524@ntu.edu.tw](mailto:r08521524@ntu.edu.tw)  
🔗 LinkedIn: [HAOYU YANG](https://www.linkedin.com/in/ntuhyu)  

## Acknowledgments
- A final project for [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) by [DataTalks.Club](http://datatalks.club/)
- Dataset from [Kaggle Grocery Sales Database](https://www.kaggle.com/datasets/andrexibiza/grocery-sales-dataset)
