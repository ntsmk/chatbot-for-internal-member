# Storage Bucket
resource "google_storage_bucket" "chatbot_bucket" {
    name = "${var.project_id}-chatbot-bucket"
    location = "us-central1"
    force_destroy = true
}

# Artifact Registry for Docker images
# todo add here

# Cloud Run Service with Docker image URL
# todo add here