variable "region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "name" {
  description = "Name of the service and its ECR repository"
  type        = string
  default     = "pr-checks-demo"
}
