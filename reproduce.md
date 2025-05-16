# How to Run This Project
## Prerequisites
- Clone this project.
- Ensure you have a GCP, a DBT cloud and a Kaggle account.
- Clone this project to local drive for cloud services build-up.
- Prepare credentials API keys.
    - Store GCP credentials API key with GCE admin role and GCS admin role in `./secrets`.
    - Store GCP credentials API key with GCS admin role and GBQ admin role in `./airflow/google`.
    - Store Kaggle API key in `./airflow/dags/.kaggle`
- Edit `variables.yaml` and `connections.yaml` in `./secrets` folder to ensure your cloud resource are all set up properly.

```
For GCP Credentials you can refer [here](https://cloud.google.com/docs/authentication/api-keys#create) for instructions. 
Ensure proper IAM role was given to the user.

For Kaggle API Key Refer [here](https://www.kaggle.com/docs/api) for instructions. 
```

## Files
- `/airflow` : 
    - `/dags` :
        - `/.kaggle` : Storge credential key for Kaggle API.
        - `/helper` :
            - `variables.py` : Store global variables will be imported in other scripts.
            - `read_load.py` : Functions to load data to Google Cloud Storage and BigQuery.
            - `task_functions.py` : Functions used in the Airflow DAG.
        - `batch_data_etl.py` : Orcorchestrating a daily pipeline to run ELT batch process for sales summary and more.
        - `batch_spark.py` : Orcorchestrating a weekly pipeline to build customer segmentation models and create a recommendation table.
    - `/google` : Storge credential key for accessing GCP service (GBQ,GCS).
    - `Dockerfile` : Customize docker image for Airflow service.
    - `requirements.txt` : Python package that will be installed during docker image build phase and used in the pipeline.
- `spark`:
    - `raw_data_schema.py` : Define data schema to prevent reading error.
    - `raw_to_silver.py` : Create `stg_recommend` model.
    - `rfm_model.py` : Create `stg_recommend` model.
    - `silver_to_gold.py` : Create `mart_recommend` model.
- `/dbt` : 
    - `models` :
        - `gold_layer` : Build mart tables: mart_sales_summary, mart_customer_behavior, mart_employee_performance
        - `silver_layer` : Build staging model and dimensional models including: stg_sales, dim_customers, dim_employees, dim_products
    - `seeds` : Load static, infrequently changing data into data warehouse.
    - `dbt_project.yml` : Declare general setting in DBT project.
    - `package.yml` : Declare the external DBT packages your project depends on.
- `/secrets` : Storge credential key for building GCP service (GCE,GCS).
    - `variables.yaml` : Variables will be used in Airflow.
    - `connections.yaml` : Connections will be used in Airflow.
- `/terraform` : 
    - `main.tf` : Declare resources needed to build.
    - `variables.tf` : Store key variables for GCP service.
- `docker-compose.yaml` : Building Airflow docker service and its dependent services on GCE.

## Reproducing
1. Cloud resources provision
    - In this step your are going to build two google compute engines, one google storage bucket.
    - Update the terraform `main.tf` `variable.tf` with your GCP project ID and desired resource configurations before running these commands.
    - To build cloud resource you need a [Local Setup for Terraform and GCP](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform/1_terraform_gcp)
    - Run `terraform init` then `terraform plan` and finally `terraform apply`.
2. Prepare DBT production environment
    - Make sure you have a **Team** DBT cloud account so that you can use API to trigger jobs created in DBT cloud.
    - Make connections with your cloud data warehouse service.
    - Create a project and connected to your forked project.
    - Create a production environment and make sure to create a service token which you will need in the Airflow UI connection setting.
    - You can create jobs which can be triggered by Airflow and remember to copy all the jobs ID to `variables.json`.
3. Prepare Spark production environment
    - Make sure the virtual machine that will be used for Spark has been built, and clone this project on that VM.
    - After that, run the shell script called `install_spark.sh` in order to install Spark and Livy.
    - In order to trigger Spark jobs through Airflow, this project uses Apache Livy as a Spark endpoint. Go to the connection setting in Airflow UI, and in here you need to add a connection to this Spark VM.
4. Building Airflow service
    - Make sure the virtual machine that will be used for Airflow has been built, and now you need to clone this project on that VM. After that, run the shell script called `run_airflow.sh` in order to install docker.
    - After docker is installed, go to `./Grocery-Sales-Analysis` and run the command below to start Airflow service.
        - `docker compose up airflow-init`
        - `docker compose up -d`
    - When all containers are up and healthy, you should able to visit the Airflow UI from http://**your VM external IP**:8080.
5. Trigger ELT pipeline in Airflow UI
    - Once all the services are set, and we are ready to go.
    - Since the dataset I used is a historical data, so you've to trigger the pipeline on your own.
    - Now visit the dags you created and trigger pipeline in Airflow UI.
5. Building your own dashboard
    - Visit [Looker Studio](https://lookerstudio.google.com/) and start to build your dashboard.