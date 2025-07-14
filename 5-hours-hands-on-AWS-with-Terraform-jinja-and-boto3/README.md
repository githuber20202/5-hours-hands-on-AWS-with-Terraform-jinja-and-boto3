# AWS Automation with Terraform, Jinja2, and Boto3

## 🎯 Objective
This tool generates and applies Terraform configurations dynamically using user inputs, and validates AWS resource creation with Boto3.

## 📦 Project Structure
- `main.py` – Python entry point
- `terraform_template.j2` – Jinja2 template for Terraform
- `generated.tf` – Terraform file generated dynamically
- `aws_validation.json` – Output of verification with boto3
- `README.md` – Project documentation

## 🚀 How to Run
1. Activate virtualenv
2. Run `main.py`
3. Follow prompts to select AWS AMI, instance type, etc.
4. Terraform will be executed automatically
5. Validation results will be saved to `aws_validation.json`

## 🔁 Cleanup
To destroy all created resources, re-run the script and choose `destroy`.

## ✅ Requirements
- Python 3.7+
- AWS credentials configured via CLI or environment variables
- Terraform CLI installed
