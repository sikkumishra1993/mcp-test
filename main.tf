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

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "jenkins_sg" {
  name        = "jenkins-terraform-sg"
  description = "Security group for Jenkins Terraform EC2"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name      = "Jenkins-Terraform-SG"
    ManagedBy = "Terraform"
  }
}

resource "aws_instance" "jenkins_ec2" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = tolist(data.aws_subnets.default.ids)[0]
  
  vpc_security_group_ids = [aws_security_group.jenkins_sg.id]
  
  tags = {
    Name        = "Jenkins-Terraform-EC2"
    Environment = "Development"
    ManagedBy   = "Terraform"
    CreatedBy   = "Jenkins-Pipeline"
    BuildNumber = "3"
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

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.jenkins_sg.id
}
