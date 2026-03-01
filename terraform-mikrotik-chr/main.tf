provider "aws" {
  region = var.region
}

terraform {
  required_version = ">=1.2"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
  }
}

############################
# VPC
############################
resource "aws_vpc" "mikrotik_vpc" {
  cidr_block = "11.0.0.0/16"

  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "mikrotik-vpc-Lab"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.mikrotik_vpc.id

  tags = {
    Name = "mikrotik-igw"
  }
}

resource "aws_subnet" "public_subnet_mikrotik" {
  vpc_id                  = aws_vpc.mikrotik_vpc.id
  cidr_block              = "11.0.1.0/24"
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = true

  tags = {
    "Name" = "public-subnet-mikrotik"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.mikrotik_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "route-public-mikrotik"
  }
}

resource "aws_route_table_association" "public_zone1" {
  subnet_id      = aws_subnet.public_subnet_mikrotik.id
  route_table_id = aws_route_table.public.id
}

############################
# Security Group
############################
resource "aws_security_group" "mikrotik_lab" {
  name        = "mikrotik_lab"
  description = "Allow mikrotik traffic vpn"
  vpc_id      = aws_vpc.mikrotik_vpc.id

  tags = {
    Name = "mikrotik_lab"
  }
}

/*
resource "aws_vpc_security_group_ingress_rule" "allow_winbox" {
  security_group_id = aws_security_group.mikrotik_lab.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 8291
  to_port           = 8291
}

resource "aws_vpc_security_group_ingress_rule" "allow_ipsec" {
  security_group_id = aws_security_group.mikrotik_lab.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "udp"
  from_port         = 500
  to_port           = 500
}

resource "aws_vpc_security_group_ingress_rule" "allow_ipsec_2" {
  security_group_id = aws_security_group.mikrotik_lab.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "udp"
  from_port         = 4500
  to_port           = 4500
}*/

resource "aws_vpc_security_group_ingress_rule" "allow_all_inbound_ipv4" {
  security_group_id = aws_security_group.mikrotik_lab.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

resource "aws_vpc_security_group_egress_rule" "allow_all_outbound_ipv4" {
  security_group_id = aws_security_group.mikrotik_lab.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

############################
# EC2 Instance
############################
resource "aws_instance" "mikrotik_chr_instance" {
  ami                         = "ami-0989af5bf0021a8ae"
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.public_subnet_mikrotik.id
  vpc_security_group_ids      = [aws_security_group.mikrotik_lab.id]
  associate_public_ip_address = true
  source_dest_check           = false

  tags = {
    Name = "Mikrotik CHR Lab"
  }
}

############################
# Elastic IP
############################
resource "aws_eip" "mikrotik_eip" {
  domain = "vpc"

  tags = {
    Name = "mikrotik-eip"
  }
}

resource "aws_eip_association" "mikrotik_eip_assoc" {
  instance_id   = aws_instance.mikrotik_chr_instance.id
  allocation_id = aws_eip.mikrotik_eip.id
}
