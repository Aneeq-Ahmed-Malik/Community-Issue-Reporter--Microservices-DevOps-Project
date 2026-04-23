output "vpc_id" {
  description = "ID of the provisioned VPC."
  value       = aws_vpc.this.id
}

output "public_subnet_id" {
  description = "ID of the public subnet."
  value       = aws_subnet.public.id
}

output "ec2_public_ip" {
  description = "Public IP of the Kubernetes host EC2 instance."
  value       = aws_instance.cluster_host.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS of the Kubernetes host EC2 instance."
  value       = aws_instance.cluster_host.public_dns
}

output "ssh_command" {
  description = "SSH command template for the host."
  value       = "ssh ubuntu@${aws_instance.cluster_host.public_ip}"
}

output "ansible_inventory_host" {
  description = "Inventory line for Ansible host definition."
  value       = "cluster ansible_host=${aws_instance.cluster_host.public_ip} ansible_user=ubuntu"
}
