# Creating Storage Bucket in GCP
# it complains there is already existing bucket. I deleted it
resource "google_storage_bucket" "chatbot_bucket" {
    name = "${var.project_id}-chatbot-bucket"
    location = "us-central1"
    force_destroy = true
}

# Creating Artifact Registry for Docker images in GCP
# Got error, on GUI console, enabled it manually
# Also it complains there is already existing registry. I deleted it
resource "google_artifact_registry_repository" "chatbot_repo"{
    provider = google
    location = "us-central1"
    repository_id = "chatbot"
    description = "Docker repository for chatbot app"
    format = "DOCKER"

}

# Creating Cloud Run Service with Docker image URL in GCP
# repository_id = <REPO_NAME>
# Enabled Cloud Run Admin API manually
resource "google_cloud_run_service" "chatbot_service" {
  name     = "chatbot"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/cloudrun/hello" # placeholder
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.chatbot_service.location
  service  = google_cloud_run_service.chatbot_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
