resource "aws_security_group" "webdev_lab" {
  name        = "webdev_lab"
  description = "Allow only from vpc"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "webdev_lab"
  }
}

resource "aws_vpc_security_group_ingress_rule" "allow_http_ipv4" {
  security_group_id = aws_security_group.webdev_lab.id
  cidr_ipv4         = aws_vpc.main.cidr_block
  from_port         = 80
  ip_protocol       = "tcp"
  to_port           = 80
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.webdev_lab.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

resource "aws_instance" "webserver_instance" {
  ami                         = "ami-0f3caa1cf4417e51b" # us-east-1
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.private_zone1.id
  vpc_security_group_ids      = [aws_security_group.webdev_lab.id]
  associate_public_ip_address = false
  iam_instance_profile        = "SSMInstanceProfile"

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html
              EOF

  tags = {
    Name = "Web Server Lab"
  }
}