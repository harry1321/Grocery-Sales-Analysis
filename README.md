# Retail Sales Data Engineering Pipeline

---

<div align="center">

[Problem Statement](#problem-statement) •
[Solution](#solution) •
[Project Details](#project-details) •
[Data Pipeline Architecture](#data-pipeline-architecture) <br>
[Running the Project](#running-the-project) •
[Dashboard](#dashboard) • 
[Contact](#contact-information) • 
[Awesome Resources](#awesome-resources)
</div>

---

This project builds a data engineering pipeline to analyze grocery sales data and produce an interactive dashboard. The dashboard enables us to explore revenue by cities, assess customer purchasing patterns, and evaluate salesperson performance to uncover key drivers behind sales trends.

The Grocery Sales Dataset, sourced from Kaggle, comprises seven interconnected tables covering transactional, customer, product, and geographic data. The dataset includes detailed records of product categories, customers’ personal and location information, product attributes, employee details, and a comprehensive sales log. The data spans a four-month period and provides a rich foundation for analyzing consumer behavior, sales performance, and regional sales distribution.

## Problem Statement

This dashboard aims to tackle real-world business challenges such as understanding customer purchasing patterns, evaluating sales team effectiveness, and identifying high-performing regions. Specifically, the goal is to enable data-driven decisions that optimize marketing strategies, improve customer retention, and allocate sales resources more effectively.

The problem statement focuses on three core areas:
- Customer Purchase Behavior — Who are our repeat customers, and how much do they spend? What kind of product creates most revenue and what is the porpotion of each product category?
- Salesperson Effectiveness — Which employees are driving the most value?
- Geographic Sales Insights — Where are the sales hotspots across cities?

## Solution

This pipeline will automatically process data and prepare tables for analysis in Google BigQuery, which wil then be used to build a dashboard. The dashboard presents five charts directly aligned with the problem statement. 
It includes：
- A bar chart presents top 10th ranking cities by total revenue
- A bar chart shows top 10th employees ranking by sales over time
- A bar chart shows top 10th customers ranking by total order value over time
- A line chart shows the sales trend over time
- A pie chart illustrates sales revenue distribution across product categories

Additionally, customer segmentation is visualized through metrics such as total spending and average order value. These visualizations collectively provide insights into sales dynamics, team performance, and customer behavior, making the dashboard a powerful tool for strategic planning and operational decision-making.

## Project Details
This project proposes a data engineering pipeline that automates the data processing workflow utilizing the following tech stacks:
- [`Airflow`](https://airflow.apache.org/) for data pipeline orchestration
- `Google Cloud Platform (GCP)` services for data lake, data warehouse and virtual machine
- [`DBT`](https://www.getdbt.com/) for data modeling and transformation
- [`Terraform`](https://github.com/hashicorp/terraform) for cloud resources provision
- `Looker Studio` for building dashboard

### Data Pipeline Architecture

This pipeline contains the following parts of precessing data:
- **Data Extraction**: Download data files from [Kaggle Grocery Sales Database](https://www.kaggle.com/datasets/andrexibiza/grocery-sales-dataset) which consists of sales transactions, customer demographics, product details, employee records, and geographical information across multiple cities. Time period begins from January in 2018 to May 10th in 2018 and contains 6,758,125 rows of transation data.

- **Data Cleaning**: Apply a variety of rules to filter out unqualified data and employ the moving average method to impute those data points. Additionally, calculated a bad data ratio to assess data quality. Data failing to meet the threshold will undergo further review.

- **Data Loading**: Store the data into Google Cloud Storage for long term storage. Then load the simplely processed data into a BigQuery dataset, which is designated to be transformed by DBT.

- **Data Transform**: Transform the data to prepare it for analysis with DBT..


To summarize here is a snapshot from Airflow web UI to show how these job are arranged.
![architecture.png](/assets/workflow_dag.png)

And this is a lineage describing how models are built in DBT.
![lineage.png](/assets/lineage.png)

## Running the Project

### Prerequisites
- Clone this project.
- Ensure you have a GCP, a DBT cloud and a Kaggle account.
- Clone this project to local drive for cloud services build-up.
- Prepare credentials API keys.
    - Store GCP credentials API key with GCE admin role and GCS admin role in `./secrets`.
    - Store GCP credentials API key with GCS admin role and GBQ admin role in `./airflow/google`.
    - Store Kaggle API key in `./airflow/dags/.kaggle`
- Edit variables.json to ensure your cloud resource name are all set up properly.

```
For GCP Credentials you can refer [here](https://cloud.google.com/docs/authentication/api-keys#create) for instructions. 
Ensure proper IAM role was given to the user.

For Kaggle API Key Refer [here](https://www.kaggle.com/docs/api) for instructions. 
```

### Files
- `/airflow` : 
    - `/dags` :
        - `/.kaggle` : Storge credential key for Kaggle API.
        - `/helper` :
            - `variables.py` : Store global variables will be imported in other scripts.
            - `read_load.py` : Functions to load data to Google Cloud Storage and BigQuery.
            - `task_functions.py` : Functions used in the Airflow DAG.
        - `batch_data_etl.py` : Airflow DAG setup for orcorchestrating the ELT process.
    - `/google` : Storge credential key for accessing GCP service (GBQ,GCS).
    - `Dockerfile` : Customize docker image for airflow service.
    - `requirements.txt` : Python package that will be installed during docker image build phase and used in the pipeline.
    - `variables.json` : Variables will be imported in Airflow. When the airflow server is up make sure to import this file through the UI.
- `/dbt` : 
    - `models` :
        - `gold_layer` : Build fact tables: fct_sales_summary, fct_customer_behavior, fct_employee_performance
        - `silver_layer` : Build staging model and dimensional models including: stg_sales, dim_customers, dim_employees, dim_products
    - `seeds` : Load static, infrequently changing data into data warehouse.
    - `dbt_project.yml` : Declare general setting in DBT project.
    - `package.yml` : Declare the external DBT packages your project depends on.
- `/secrets` : Storge credential key for building GCP service (GCE,GCS).
- `/terraform` : 
    - `main.tf` : Declare resources needed to build.
    - `variables.tf` : Store key variables for GCP service.
- `docker-compose.yaml` : Building airflow docker service and its dependent services on GCE.

### Reproducing
1. Cloud resources provision:
    - Update the terraform `main.tf` `variable.tf` with your GCP project ID and desired resource configurations before running these commands.
    - To build cloud resource you need a [Local Setup for Terraform and GCP](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform/1_terraform_gcp)
    - Run `terraform init` then `terraform plan` then `terraform apply`.
2. Prepare DBT production environment:
    - Make sure you have a **Team** DBT cloud account so that you can use API to trigger jobs created in DBT cloud.
    - Make connections with your cloud data warehouse service.
    - Create a project and connected to your forked project.
    - Create a production environment and make sure to create a service token which you will need in the airflow UI connection setting.
    - You can create jobs which can be triggered by airflow and remember to copy all the jobs ID to `variables.json`.
3. Building airflow service:
    - The cloud resources have already been built in step 1, and now you need to access into the VM and clone this project. After that, run the shell script called `run_airflow.sh` in order to install docker.
    - After docker is installed, go to `./Retail-Promo-Analysis` and run the command below.
        - `docker compose up airflow-init`
        - `docker compose up -d`
    - When all containers are up and healthy, you now can visit the airflow UI from http://**your VM external IP**:8080.
    - Go to the variables setting in airflow UI, and upload the `variables.json` under airflow directory.
    - Go to the connection setting in airflow UI, and in here you need to add a connection to your DBT cloud. For more instructions go to [Guides to Airflow and dbt Cloud](https://docs.getdbt.com/guides/airflow-and-dbt-cloud?step=1)
4. Trigger ELT pipeline in airflow UI.
    - Once all the services are set, and we are ready to go.
    - Since the dataset I used is a historical data, so you've to trigger the pipeline on your own.
    - Now visit the dags you created and trigger pipeline in airflow UI.
5. Building your own dashboard
    - Visit [Looker Studio](https://lookerstudio.google.com/) and start to build your dashboard.

## Dashboard
You can access this dashboard from [here](https://lookerstudio.google.com/s/jEFS_2hqVB0).

<p align="center">
    <img src="/assets/dashboard_snap.png" width="60%", height="60%">
    <em></em>
</p>

## Contact Information
📧 Email: [r08521524@ntu.edu.tw](mailto:r08521524@ntu.edu.tw)  
🔗 LinkedIn: [HAOYU YANG](https://www.linkedin.com/in/ntuhyu)  

Feel free to reach out!

## Acknowledgments
- A final project for [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) by [DataTalks.Club](http://datatalks.club/)
- Dataset from [Kaggle Grocery Sales Database](https://www.kaggle.com/datasets/andrexibiza/grocery-sales-dataset)
