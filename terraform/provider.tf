# provider.tf

terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "~> 5.0"

            }

        }

}

provider "google" {
    project = "<need to fill out later, GCP_PROJECT_ID>"
    region = "fill out region later"
    }