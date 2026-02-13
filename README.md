# Terraform EC2 Instance

This Terraform configuration creates an EC2 instance in AWS.

## Resources Created

- EC2 Instance: t3.micro instance with Amazon Linux 2023
- Region: ap-south-1 (Mumbai)
- Storage: 20GB encrypted GP3 volume

## Usage

Initialize: terraform init
Plan: terraform plan
Apply: terraform apply
Destroy: terraform destroy

## Variables

- aws_region: AWS region (default: ap-south-1)
- instance_type: EC2 instance type (default: t3.micro)
- ami_id: AMI ID to use (default: Amazon Linux 2023)

## Outputs

- instance_id: The ID of the created EC2 instance
- instance_public_ip: Public IP address
- instance_private_ip: Private IP address

Created by Jenkins Pipeline
