# Define the AWS provider
provider "aws" {
  region = "us-west-2"
}

# Create a VPC with syntax error
resource "aws_vpc" "main_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "${var.name}-vpc"  # Undefined variable
  }
}

# Create public subnet with invalid reference
resource "aws_subnet" "public_subnet" {
  vpc_id            = aws_vpc.nonexistent_vpc.id  # Invalid reference
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "public_subnet"
  }
}

# Create an EC2 instance with multiple errors
resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.main_sg.id]

  tags = {
    Name = $var.name-web_server  # Syntax error in interpolation
  }

  user_data = <<-EOF  # Incorrect EOF indentation
    #!/bin/bash
    echo "Hello, World!"
  EOF
}

# Output with invalid reference
output "web_server_public_ip" {
  value = aws_instance.nonexistent_server.public_ip  # Invalid reference
}
