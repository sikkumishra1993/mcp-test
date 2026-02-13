# Terraform EC2 Instance

This Terraform configuration creates an EC2 instance in AWS with VPC and Security Group.

## Resources Created

- EC2 Instance: t2.micro instance with Amazon Linux 2023
- Security Group: Allows SSH access (port 22)
- Default VPC: Uses default VPC and subnet
- Region: us-east-1 (Virginia)
- Storage: 20GB encrypted GP3 volume

## Usage

Initialize: terraform init
Plan: terraform plan
Apply: terraform apply
Destroy: terraform destroy

## Variables

- aws_region: AWS region (default: us-east-1)
- instance_type: EC2 instance type (default: t2.micro)
- ami_id: AMI ID to use (default: Amazon Linux 2023)

## Outputs

- instance_id: The ID of the created EC2 instance
- instance_public_ip: Public IP address
- instance_private_ip: Private IP address
- security_group_id: ID of the security group

Created by Jenkins Pipeline
