variable "gcp_credentials" {
    description = "Google Cloud service account credentials JSON"
    type = string
}

variable "project_id" {
    description = "The GDP project ID"
    type = string
}

variable "port" {
  description = "Port the web server listens on"
  type        = number
  default     = 8080
}

variable "google_ai_api_key" {
  description = "Google AI API key for Gemini"
  type        = string
  sensitive   = true
}

variable "supabase_url" {
  description = "Supabase project URL"
  type        = string
}

variable "supabase_service_key" {
  description = "Supabase service role key"
  type        = string
  sensitive   = true
}