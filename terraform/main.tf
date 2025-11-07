terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "nhs-appointments-terraform-state"
    key    = "terraform.tfstate"
    region = "eu-west-2"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "NHS-Appointments"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "nhs-appointments"
}

# S3 bucket for frontend hosting
resource "aws_s3_bucket" "frontend" {
  bucket = "${var.project_name}-frontend-${var.environment}"
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100"

  origin {
    domain_name = aws_s3_bucket_website_configuration.frontend.website_endpoint
    origin_id   = "S3-${aws_s3_bucket.frontend.id}"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.frontend.id}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# DynamoDB tables
resource "aws_dynamodb_table" "appointments" {
  name           = "${var.project_name}-appointments-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "appointment_id"

  attribute {
    name = "appointment_id"
    type = "S"
  }

  attribute {
    name = "patient_id"
    type = "S"
  }

  attribute {
    name = "practice_id"
    type = "S"
  }

  attribute {
    name = "appointment_date"
    type = "S"
  }

  global_secondary_index {
    name            = "patient-index"
    hash_key        = "patient_id"
    range_key       = "appointment_date"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "practice-index"
    hash_key        = "practice_id"
    range_key       = "appointment_date"
    projection_type = "ALL"
  }

  tags = {
    Name = "Appointments Table"
  }
}

resource "aws_dynamodb_table" "patients" {
  name           = "${var.project_name}-patients-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "patient_id"

  attribute {
    name = "patient_id"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }

  global_secondary_index {
    name            = "email-index"
    hash_key        = "email"
    projection_type = "ALL"
  }

  tags = {
    Name = "Patients Table"
  }
}

resource "aws_dynamodb_table" "practices" {
  name           = "${var.project_name}-practices-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "practice_id"

  attribute {
    name = "practice_id"
    type = "S"
  }

  tags = {
    Name = "Practices Table"
  }
}

# Cognito User Pool
resource "aws_cognito_user_pool" "main" {
  name = "${var.project_name}-users-${var.environment}"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true
  }

  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = false
  }

  schema {
    name                = "nhs_number"
    attribute_data_type = "String"
    required            = false
    mutable             = true
  }

  schema {
    name                = "role"
    attribute_data_type = "String"
    required            = false
    mutable             = true
  }

  tags = {
    Name = "User Pool"
  }
}

resource "aws_cognito_user_pool_client" "main" {
  name         = "${var.project_name}-client-${var.environment}"
  user_pool_id = aws_cognito_user_pool.main.id

  explicit_auth_flows = [
    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH"
  ]

  prevent_user_existence_errors = "ENABLED"
}

# Outputs
output "frontend_bucket" {
  value = aws_s3_bucket.frontend.id
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.frontend.id
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.frontend.domain_name
}

output "user_pool_id" {
  value = aws_cognito_user_pool.main.id
}

output "user_pool_client_id" {
  value = aws_cognito_user_pool_client.main.id
}

output "dynamodb_tables" {
  value = {
    appointments = aws_dynamodb_table.appointments.name
    patients     = aws_dynamodb_table.patients.name
    practices    = aws_dynamodb_table.practices.name
  }
}
