from airflow.models import Variable
# Should be using Airflow Variable to get these Global Vars.
# Which are already been setup in the docker-compose.yaml file
# ex: AWS_S3_BUCKET = Variable.get("AWS_S3_BUCKET")
# https://cloud.google.com/storage/docs/samples/storage-transfer-manager-upload-directory#storage_transfer_manager_upload_directory-python
GCP_CREDENTIALS_FILE_PATH = Variable.get("GCP_CREDENTIALS_FILE_PATH")
GCP_PROJECT_ID = Variable.get('GCP_PROJECT_ID')
BUCKET_NAME = Variable.get('BUCKET_NAME')
BUCKET_CLASS = Variable.get('BUCKET_CLASS')
BUCKET_LOCATION = Variable.get('BUCKET_LOCATION')
