project_name       = "community-issues"
environment        = "dev"
aws_region         = "us-east-1"
instance_type      = "c7i-flex.large"
key_pair_name      = "cloud_project"
admin_cidr         = "203.0.113.10/32"
public_subnet_cidr = "10.40.1.0/24"
vpc_cidr           = "10.40.0.0/16"

tags = {
  Owner = "Aneeq-Malik"
}
