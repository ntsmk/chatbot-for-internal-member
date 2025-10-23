# Storage Bucket
resource "google_storage_bucket" "chatbot_bucket" {
    name = "${var.project_id}-chatbot-bucket"
    location = var.region
    force_destroy = true
}

# Artifact Registry for Docker images


# Cloud Run Service with Docker image URL