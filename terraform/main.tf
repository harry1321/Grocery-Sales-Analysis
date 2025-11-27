# This file will create a GCE VM for running airflow, 
# a GCS bucket to store raw csv files, 
# and create a firewall policy in order to visit airflow UI at 8080.
provider "google" {
  credentials = file(var.credential)
  project     = var.project_id
  region      = var.region
}

# build service account for airflow gce
resource "google_service_account" "airflow_gce" {
  account_id   = "airflow-gce"
  display_name = "Service Account for Airflow GCE"
}

# IAM Bindings for airflow gce
locals {
  airflow_roles = [
    "roles/secretmanager.secretAccessor",
    "roles/bigquery.admin",
    "roles/storage.admin"
  ]
}

resource "google_project_iam_member" "airflow_gce_roles" {
  for_each = toset(local.airflow_roles)
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.airflow_gce.email}"
}

resource "google_compute_instance" "airflow-instance" {
  # name your GCE VM
  name         = "airflow-instance"
  machine_type = "e2-standard-8"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size  = 80
    }
  }

  network_interface {
    network = "default"
    access_config {} # 允許外部訪問
  }

  # using ADC to grant authorization
  service_account {
    email  = google_service_account.airflow_gce.email
    scopes = ["cloud-platform"]
  }

  tags = ["airflow"]
  
  depends_on = [ 
    google_project_iam_member.airflow_gce_roles 
  ]
}

resource "google_compute_firewall" "allow_airflow_ports" {
  name    = "allow-airflow-ports"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }
  
  target_tags = ["airflow"]
  source_ranges = ["0.0.0.0/0"] # You can change to your computer IP
}

resource "google_storage_bucket" "raw-data-bucket" {
  name     = "${var.project_id}-raw-data-westus1"
  location = "US-WEST1"
  storage_class = "STANDARD"
}

output "airflow_webserver_url" {
  value       = "http://${google_compute_instance.airflow-instance.network_interface.0.access_config.0.nat_ip}:8080"
  description = "Airflow UI 的訪問網址"
}

# enable secret manager api
resource "google_project_service" "secret_manager_api" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_iam_member" "airflow_gce_roles" {
  for_each = toset(local.airflow_roles)
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.airflow_sa.email}"
}

# setup livy api connection secret
resource "google_secret_manager_secret" "livy_conn" {
  secret_id = "airflow-connections-livy"
  
  replication {
    auto {}
  }
  depends_on = [google_project_service.secret_manager_api]
}

resource "google_secret_manager_secret_version" "livy_conn_val" {
  secret = google_secret_manager_secret.livy_conn.id
  secret_data = var.livy_conn_uri
}

# setup DBT api connection secret
resource "google_secret_manager_secret" "dbt_conn" {
  secret_id = "airflow-connections-dbt_default"
  
  replication {
    auto {}
  }
  depends_on = [google_project_service.secret_manager_api]
}

resource "google_secret_manager_secret_version" "dbt_conn_val" {
  secret = google_secret_manager_secret.dbt_conn.id
  secret_data = var.dbt_conn_uri
}


# setup livy api connection secret
resource "google_secret_manager_secret" "livy_conn" {
  secret_id = "airflow-connections-livy"
  
  replication {
    auto {}
  }
  depends_on = [google_project_service.secret_manager_api]
}

resource "google_secret_manager_secret_version" "livy_conn_val" {
  secret = google_secret_manager_secret.livy_conn.id
  secret_data = var.livy_conn_uri
}

# setup DBT api connection secret
resource "google_secret_manager_secret" "dbt_conn" {
  secret_id = "airflow-connections-dbt_default"
  
  replication {
    auto {}
  }
  depends_on = [google_project_service.secret_manager_api]
}

resource "google_secret_manager_secret_version" "dbt_conn_val" {
  secret = google_secret_manager_secret.dbt_conn.id
  secret_data = var.dbt_conn_uri
}

resource "google_secret_manager_secret" "airflow_vars" {
  for_each = var.airflow_variables_map
  
  # Secret ID 格式：airflow-variables-VARIABLE_NAME
  secret_id = "airflow-variables-${each.key}" 
  
  replication {
    auto {}
  }
  depends_on = [google_project_service.secret_manager_api]
}

resource "google_secret_manager_secret_version" "airflow_vars_version" {
  for_each = var.airflow_variables_map
  
  secret      = google_secret_manager_secret.airflow_vars[each.key].id
  secret_data = each.value
}
