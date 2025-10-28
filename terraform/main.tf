# # Creating Storage Bucket in GCP
# # it complains there is already existing bucket. I deleted it
# resource "google_storage_bucket" "chatbot_bucket" {
#     name = "${var.project_id}-chatbot-bucket"
#     location = "us-central1"
#     force_destroy = true
# }
#
# # Creating Artifact Registry for Docker images in GCP
# # todo need to run this remotely, and check if repository is created?
# # Got error, on GUI console, enabled it
# # Also it complains there is already existing registry. I deleted it
# resource "google_artifact_registry_repository" "chatbot_repo"{
#     provider = google
#     location = "us-central1"
#     repository_id = "chatbot"
#     description = "Docker repository for chatbot app"
#     format = "DOCKER"
#
# }

# Creating Cloud Run Service with Docker image URL in GCP
# todo add here
# repository_id = <REPO_NAME>
resource "google_cloud_run_service" "chatbot_service" {
    name = "chatbot-service"
    location = "us-central1"

    template {
        spec{
            containers{
                # docker image in Articraft Registry
                image = "us-central1-docker.pkg.dev/${var.project_id}/chatbot/chatbot:lastest"
                ports { container_port = 8080 }
            }
        }
    }

    traffic{
        percent = 100
        latest_revision = true
    }
}

resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.chatbot_service.location
  service  = google_cloud_run_service.chatbot_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}