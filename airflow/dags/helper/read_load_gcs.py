import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from google.cloud import storage
from google.cloud import bigquery
from google.cloud.bigquery import SchemaField

from helper.variables import GCP_CREDENTIALS_FILE_PATH, GCP_PROJECT_ID, BUCKET_NAME, BUCKET_CLASS, BUCKET_LOCATION

class GCSTools():
    def __init__(self, credentials_file=GCP_CREDENTIALS_FILE_PATH):
        self.storage_client = storage.Client.from_service_account_json(credentials_file)

    def info(self):
        print(f"This is a GCSTools with gcp_credentials_file locates in {GCP_CREDENTIALS_FILE_PATH}")

    def list_buckets(self):
        """ Lists all buckets. """
        for bucket in self.storage_client.list_buckets():
            print(bucket.name)
    
    def create_bucket(self, bucket_name):
        """
        Create a new bucket in the US region with the standard storage class.
        """
        bucket = self.storage_client.bucket(bucket_name)
        bucket.storage_class = BUCKET_CLASS
        new_bucket = self.storage_client.create_bucket(bucket, location=BUCKET_LOCATION)

        print(f"Created bucket {new_bucket.name} in {new_bucket.location} with storage class {new_bucket.storage_class}")
        
        return new_bucket

class GCSBucket(GCSTools):
    def __init__(self, bucket_name=BUCKET_NAME):
        super().__init__()
        self.bucket_name = bucket_name
        self.bucket = self.storage_client.bucket(bucket_name)
    
    def info(self):
        print(f"This is a GCSBucket under GCSTools with bucket name: {self.bucket_name}")
    
    def set_bucket_name(self, name):
        """ Change the target bucket """
        self.bucket_name = name
        self.bucket = self.storage_client.bucket(name)

    def list_files(self,prefix,suffix='.'):
        """ Lists all blobs with prefix. """
        blobs = self.bucket.list_blobs(prefix=prefix)
        temp = [blob.name for blob in blobs if f'{suffix}' in blob.name] 
        return temp

    def check(self, blob_name):
        """ Check a file exsists or not """
        return storage.Blob(bucket=self.bucket, name=blob_name).exists(self.storage_client)

    def delete(self):
        """ Delete a file in bucket """
        pass

    def retrieve_object_from_bucket(self, object_name, destination_file_path):
        
        """
            project_id (str): Your Google Cloud project ID.
            bucket_name (str): The name of the GCS bucket.
            object_name (str): The name of the object you want to retrieve.
            destination_file_path (str): The path to save the retrieved object locally.
        """
        
        try:
            # Get the blob (object) from the bucket
            blob = self.bucket.blob(object_name)

            # Download the blob to the specified file path
            blob.download_to_filename(destination_file_path)

            print(f"Object '{object_name}' retrieved and saved to '{destination_file_path}'.")

        except Exception as e:
            print(f"Error: {e}")

    def upload_file(self, local_file_path, remote_file_name):
        """ Upload the file to self.bucket """
        blob = self.bucket.blob(remote_file_name)
        blob.upload_from_filename(local_file_path)
        print(f"File {local_file_path} uploaded to gs://{self.bucket_name}/{remote_file_name}")

    def upload_directory(self, source_directory, prefix):
        # First, recursively get all files in `directory` as Path objects.
        directory_as_path_obj = Path(source_directory)
        paths = directory_as_path_obj.rglob("*")

        # Filter so the list only includes files, not directories themselves.
        file_paths = [path for path in paths if path.is_file()]

        # These paths are relative to the current working directory. Next, make them
        # relative to `directory`
        relative_paths = [path.relative_to(source_directory) for path in file_paths]

        # Finally, convert them all to strings.
        string_paths = [f"{prefix}/{str(path)}" for path in relative_paths]

        print(f"Found {len(string_paths)} files.")

        # Start the upload.
        for local_file_path, remote_file_name in zip(file_paths, string_paths):
            self.upload_file(local_file_path, remote_file_name)

class GCBigQuery():
    def __init__(self, dataset_name, credentials_file=GCP_CREDENTIALS_FILE_PATH):
        self.bq_client = bigquery.Client.from_service_account_json(credentials_file)
        self.dataset_name = dataset_name
    
    def load_from_bucket(self, table_name, bucket_name, prefix):
        temp_gcs = GCSBucket(bucket_name)
        result_df = pd.DataFrame()
        blobs = temp_gcs.list_files(prefix=prefix, suffix='.csv')

        for blob in blobs:
            temp = pd.read_csv(f"gs://{temp_gcs.bucket_name}/{blob}", encoding = 'big5', storage_options={"token": GCP_CREDENTIALS_FILE_PATH})
            temp = pd.melt(temp, id_vars=temp.columns.tolist()[0], value_vars=temp.columns.tolist()[1:], var_name="vd", value_name=blob.split('_')[1])
            try:
                result_df = pd.merge(result_df, temp , on=temp.columns.tolist()[0:2], how="outer")
            except KeyError:
                result_df = temp
                continue

        job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.CSV,
                    skip_leading_rows=1,
                    schema=SCHEMA,
                    create_disposition="CREATE_IF_NEEDED",
                    write_disposition="WRITE_APPEND",
                    time_partitioning=bigquery.TimePartitioning(field="time"),
                    clustering_fields=["vd"]
                )
        job = self.bq_client.load_table_from_dataframe(
            result_df, f"{GCP_PROJECT_ID}.{self.dataset_name}.{table_name}", job_config=job_config
        )
        job.result()

        if job.done():
            print(f"Total files of {len(blobs)} in {temp_gcs.bucket_name}/{prefix} successfully uploaded to {self.dataset_name}.{table_name}")
        
        """
        # load from google storage
        job = self.bq_client.load_table_from_uri(
            blob.name, f"{self.dataset_name}.{table_name}", job_config=job_config
        )
        job.result()

        if job.Done:
            print(f"File {blob.name} successfully uploaded to {self.dataset_name}.{table_name}")
        """

    def generate_bigquery_schema(self,df: pd.DataFrame):
        # https://medium.com/@danilo.drobac/auto-generate-bigquery-schema-from-a-pandas-dataframe-603f09ecad8b
        TYPE_MAPPING = {
            "i": "INTEGER",
            "u": "NUMERIC",
            "b": "BOOLEAN",
            "f": "FLOAT",
            "O": "STRING",
            "S": "STRING",
            "U": "STRING",
            "M": "TIMESTAMP",
        }
        schema = []
        for column, dtype in df.dtypes.items():
            val = df[column].iloc[0]
            mode = "REPEATED" if isinstance(val, list) else "NULLABLE"

            if isinstance(val, dict) or (mode == "REPEATED" and isinstance(val[0], dict)):
                fields = self.generate_bigquery_schema(pd.json_normalize(val))
            else:
                fields = ()

            type = "RECORD" if fields else TYPE_MAPPING.get(dtype.kind)
            schema.append(
                SchemaField(
                    name=column,
                    field_type=type,
                    mode=mode,
                    fields=fields,
                )
            )
        return schema

    # def standard_query(self, start_date, end_date, weekdays=None, stime=None, etime=None, locations=None, table_name='test') -> str:
    #     start_date = datetime.strptime(start_date,"%Y-%m-%d")
    #     end_date = datetime.strptime(end_date,"%Y-%m-%d")
    #     clause=f"WHERE V.D >= '{start_date}' AND V.D <= '{end_date}'"
    #     if isinstance(weekdays,list):
    #         if len(weekdays) > 1:
    #             sub_clause = ""
    #             for w in weekdays[:-1]:
    #                 sub_clause += f" V.W = {w} OR"
    #             sub_clause += f" V.W = {weekdays[-1]}"
    #             clause += f" AND ({sub_clause})"
    #         else:
    #             clause += f" AND (V.W = '{weekdays[0]}')"
    #     if isinstance(stime,str):
    #         clause += f" AND V.H >= '{stime}'"
    #     if isinstance(etime,str):
    #         clause += f" AND V.H <= '{etime}'"
    #     if isinstance(locations,list):
    #         if len(locations) > 1:
    #             sub_clause = ""
    #             for l in locations[:-1]:
    #                 sub_clause += f"'{l}', "
    #             sub_clause += f"'{locations[-1]}'"
    #             clause += f" AND (V.vd IN ({sub_clause}))"
    #         else:
    #             clause += f" AND (V.vd = '{locations[0]}')"
            
    #     clause=clause+" ORDER BY V.time_tz"
    #     sql = f"""
    #         WITH V AS(
    #         SELECT *, STRING(time, "Asia/Taipei") AS time_tz, DATETIME(time, "Asia/Taipei") AS D, MOD(EXTRACT(DAYOFWEEK FROM DATETIME(time, "Asia/Taipei"))+5, 7) AS W, TIME(time, "Asia/Taipei") AS H
    #         FROM {GCP_PROJECT_ID}.{self.dataset_name}.{table_name}
    #         )
    #         SELECT time_tz, V.vd, V.volume, V.speed, V.occupancy FROM V
    #         {clause}
    #     """
    #     return sql

    # def query(self, sql) -> pd.DataFrame:
    #     query_job = self.bq_client.query(sql)
    #     query_result = query_job.to_dataframe()
    #     return query_result

# map time interval to timestamp (specify time zone)
"""
tz = timezone(timedelta(hours=8)) #設定+8時區
d = datetime(2021, 4, 6)
d = d.replace(tzinfo=tz) #指定輸入的datetime時區為+8
result = d.timestamp() # 取得timestamp
"""