# Creating Storage Bucket in GCP
# it complains there is already existing bucket. I deleted it
resource "google_storage_bucket" "chatbot_bucket" {
    name = "${var.project_id}-chatbot-bucket"
    location = "us-central1"
    force_destroy = true
}

# Creating Artifact Registry for Docker images in GCP
# todo need to run this remotely, and check if repository is created?
# Got error, on GUI console, enabled it
resource "google_artifact_registry_repository" "chatbot_repo"{
    provider = google
    location = "us-central1"
    repository_id = "chatbot"
    description = "Docker repository for chatbot app"
    format = "DOCKER"

}

# Creating Cloud Run Service with Docker image URL in GCP
# todo add here