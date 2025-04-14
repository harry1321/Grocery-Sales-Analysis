# This file will create a GCE VM for running airflow, 
# a GCS bucket to store raw csv files, 
# and create a firewall policy in order to visit airflow UI at 8080.
provider "google" {
  credentials = file(var.credential)
  project     = var.project_id
  region      = var.region
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

  tags = ["airflow"]
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
