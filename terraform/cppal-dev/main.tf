
# A terraform configuration to launch a mailman service instance

provider "google" {
  project = "boostorg-project1"
  region  = "us-central1"
  zone    = "us-central1-a"
}

resource "google_compute_address" "lists_cppal_dev_ip_address_ext" {
  name = "lists-cppal-dev-ip-address-ext"
  address_type = "EXTERNAL"
}

resource "google_compute_address" "lists_cppal_dev_ip_address_int" {
  name = "lists-cppal-dev-ip-address-int"
  address_type = "INTERNAL"
}

resource "google_compute_instance" "example" {
  machine_type               = "n2-standard-2"
  name                       = "lists-cppal-dev-2"
  tags                       = ["elasticsearch", "munin", "nrpe", "email", "http-server", "https-server", "lb-health-check", "mailman3-core", "postgres-client", "prometheus"]
  zone                       = "us-central1-a"
  boot_disk {
    auto_delete             = true
    device_name             = "lists-cppal-dev-2"
    mode                    = "READ_WRITE"
    initialize_params {
      image                       = "https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-2404-noble-amd64-v20250502a"
      size                        = 150
      type                        = "pd-balanced"
    }
  }
  network_interface {
    network                     = "default"
    network_ip                  = google_compute_address.lists_cppal_dev_ip_address_int.address
    stack_type                  = "IPV4_ONLY"
    access_config {
      nat_ip = google_compute_address.lists_cppal_dev_ip_address_ext.address
      network_tier           = "PREMIUM"
    }
  }
}

