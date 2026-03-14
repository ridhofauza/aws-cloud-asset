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
# Security Group 1
############################
resource "aws_security_group" "server_lab" {
  name        = "server_lab_sg"
  description = "Allow ping and http traffic"
  vpc_id      = aws_vpc.mikrotik_vpc.id

  tags = {
    Name = "server_lab_sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "allow_icmp_ping" {
  security_group_id = aws_security_group.server_lab.id
  cidr_ipv4         = "11.0.0.0/16"
  ip_protocol       = "icmp"
  from_port         = -1
  to_port           = -1
}

resource "aws_vpc_security_group_ingress_rule" "allow_http" {
  security_group_id = aws_security_group.server_lab.id
  cidr_ipv4         = "11.0.0.0/16"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}

resource "aws_vpc_security_group_egress_rule" "allow_all_outbound_1_ipv4" {
  security_group_id = aws_security_group.server_lab.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

############################
# Security Group 2
############################
resource "aws_security_group" "mikrotik_lab" {
  name        = "mikrotik_lab"
  description = "Allow mikrotik traffic vpn"
  vpc_id      = aws_vpc.mikrotik_vpc.id

  tags = {
    Name = "mikrotik_lab"
  }
}

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
}

resource "aws_vpc_security_group_ingress_rule" "sg_ingress_server" {
  security_group_id            = aws_security_group.mikrotik_lab.id
  referenced_security_group_id = aws_security_group.server_lab.id
  ip_protocol                  = "-1"
  from_port                    = 0
  to_port                      = 0
}

resource "aws_vpc_security_group_egress_rule" "allow_all_outbound_ipv4" {
  security_group_id = aws_security_group.mikrotik_lab.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

############################
# EC2 Instance Mikrotik
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

############################
# EC2 Instance Web Server
############################
resource "aws_instance" "web_server_instance" {
  ami                         = "ami-0f3caa1cf4417e51b" # us-east-1
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.public_subnet_mikrotik.id
  vpc_security_group_ids      = [aws_security_group.server_lab.id]
  associate_public_ip_address = true
  source_dest_check           = false
  user_data                   = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html
              EOF

  tags = {
    Name = "Web Server - Mikrotik Lab"
  }
}