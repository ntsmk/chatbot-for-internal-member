output "bucket_name" {
    description = "Name of the created GCS bucket"
    value = google_storage_bucket.chatbot_bucket.name
}

# will add output "cloud_run_url" later