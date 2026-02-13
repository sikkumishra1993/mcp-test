terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "jenkins_ec2" {
  ami           = var.ami_id
  instance_type = var.instance_type
  
  tags = {
    Name        = "Jenkins-Terraform-EC2"
    Environment = "Development"
    ManagedBy   = "Terraform"
    CreatedBy   = "Jenkins-Pipeline"
    BuildNumber = "2"
  }
  
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }
}

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.jenkins_ec2.id
}

output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.jenkins_ec2.public_ip
}

output "instance_private_ip" {
  description = "Private IP of the EC2 instance"
  value       = aws_instance.jenkins_ec2.private_ip
}
