variable "project_name" {
  description = "Project name used for tagging and naming resources."
  type        = string
  default     = "community-issues"
}

variable "environment" {
  description = "Deployment environment label."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet."
  type        = string
  default     = "10.40.1.0/24"
}

variable "admin_cidr" {
  description = "Admin CIDR allowed to SSH to EC2."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type for the Kubernetes host."
  type        = string
  default     = "t3.medium"
}

variable "key_pair_name" {
  description = "Existing AWS key pair name for SSH access."
  type        = string
}

variable "ami_id" {
  description = "Optional AMI ID override. If empty, latest Ubuntu 22.04 is used."
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags to merge with default tags."
  type        = map(string)
  default     = {}
}
