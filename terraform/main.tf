# Creating Storage Bucket in GCP
# resource "google_storage_bucket" "chatbot_bucket" {
#     name = "${var.project_id}-chatbot-bucket"
#     location = "us-central1"
#     force_destroy = true
# }
#
# # Creating Artifact Registry for Docker images in GCP
# resource "google_artifact_registry_repository" "chatbot_repo"{
#     provider = google
#     location = "us-central1"
#     repository_id = "chatbot"
#     description = "Docker repository for chatbot app"
#     format = "DOCKER"
# }

resource "google_cloud_run_service_iam_member" "public_access" {
  service  = "chatbot-service"
  location = "us-central1"
  role     = "roles/run.invoker"
  member   = "allUsers"
}

