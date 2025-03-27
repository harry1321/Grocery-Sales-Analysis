# Define the provider
provider "google" {
  credentials = file(var.credential)
  project     = var.project_id
  region      = var.region
}

resource "google_compute_instance" "airflow_vm" {
  name         = "airflow-local-instance-test"
  machine_type = "e2-micro"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size  = 30
    }
  }

  network_interface {
    network = "default"
    access_config {} # 允許外部訪問
  }

  # 使用外部啟動腳本
  metadata_startup_script = file("./gce_airflow/startup_script.sh")

  tags = ["airflow"]
}

resource "google_compute_firewall" "allow_airflow_ports" {
  name    = "allow-airflow-ports"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["8888", "8080"]
  }
  
  target_tags = ["airflow"]
  source_ranges = ["0.0.0.0/0"] # 允許來自任何 IP 的連線
}

output "jupyter_url" {
  value       = "http://${google_compute_instance.airflow_vm.network_interface.0.access_config.0.nat_ip}:8888"
  description = "Jupyter Notebook 的訪問網址"
}

output "spark_url" {
  value       = "http://${google_compute_instance.airflow_vm.network_interface.0.access_config.0.nat_ip}:8080"
  description = "Spark UI 的訪問網址"
}
