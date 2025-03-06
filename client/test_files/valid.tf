# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
}

# Create an S3 bucket
resource "aws_s3_bucket" "example_bucket" {
  bucket = "my-tf-test-bucket-28374"
  tags = {
    Name        = "My Test Bucket"
    Environment = "Dev"
  }
}

# Enable versioning for the bucket
resource "aws_s3_bucket_versioning" "versioning_example" {
  bucket = aws_s3_bucket.example_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}
