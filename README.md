# 🧱 AWS EC2 + ALB Deployment Tool using Terraform, Jinja2 & Boto3

## 📋 Table of Contents
1. [Overview](#overview)  
2. [Features](#features)  
3. [Prerequisites](#prerequisites)  
4. [Usage](#usage)  
5. [Architecture](#architecture)  
6. [Implementation Details](#implementation-details)  
7. [Security & Public Access](#security--public-access)  
8. [Clean-up / Destroy Logic](#cleanup--destroy-logic)  
9. [Validation Output](#validation-output)

## 🔍 Overview
This project does the following:
- Prompts user for AMI, instance type, region, availability zone, and ALB name  
- Generates Terraform file (`generated.tf`) using Jinja2  
- Executes `terraform init`, `plan`, `apply` via `python-terraform`  
- Handles errors and manages failure scenarios  
- Validates deployed EC2 & ALB using `boto3`  
- Saves validation result to `aws_validation.json`

## ✅ Features
- 🧠 Interactive user input with validation and defaults  
- 💾 Dynamic Terraform rendering with Jinja2  
- ⚙️ Full infrastructure lifecycle management (init → plan → apply)  
- 🛡️ Robust error handling using `try-except` and return codes  
- 🧹 Automatic destroy if Terraform execution fails  
- 🔓 Optional EC2 access via Security Group for HTTP/SSH  
- 📄 Post-deployment validation with JSON output

## ⚙️ Prerequisites
- Python 3.7+  
- Python packages: `jinja2`, `python-terraform`, `boto3`  
- Terraform installed and available in PATH  
- AWS credentials with permissions for `us-east-1` (EC2, ALB, VPC, SG, etc.)

## 🛠️ Usage

```bash
git clone <repo>
cd <repo>
pip install -r requirements.txt
python main.py
```

- Follow the prompts for AMI, instance type, AZ, and ALB name  
- System renders → terraform init/plan/apply → validates  
- If Terraform fails, infrastructure is destroyed  
- Success leads to saved JSON in `aws_validation.json`

## 🧠 Architecture

```text
get_user_input()
    ↓
render_template() → generated.tf
    ↓
run_terraform() → init/plan/apply or destroy on failure
    ↓
validate_aws_resources() → aws_validation.json
```

## 🛠️ Implementation Details
- **get_user_input()** – Handles user selection and applies defaults  
- **render_template()** – Builds the Terraform config using Jinja2  
- **run_terraform()** – Executes init/plan/apply and manages errors  
- **destroy_infrastructure()** – Destroys infra automatically on failure  
- **validate_aws_resources()** – Verifies EC2 & ALB and generates output JSON

## 🔐 Security & Public Access
Security configuration includes:
- **Load Balancer:** Allows public HTTP on port 80  
- **EC2:** Attached with Security Group allowing HTTP and SSH access  
  Enables direct access via `http://<EC2 Public IP>/` if needed.

## 🧹 Clean-up / Destroy Logic
Automatic destroy is triggered:
- ❌ When Terraform fails at any step

No manual intervention needed – resources are cleaned up automatically.

## 📄 Validation Output
The file `aws_validation.json` will look like:

```json
{
  "instance_id": "i-0123456789abcdef0",
  "instance_state": "running",
  "public_ip": "3.92.102.45",
  "load_balancer_dns": "my-alb-123456.elb.amazonaws.com"
}
```