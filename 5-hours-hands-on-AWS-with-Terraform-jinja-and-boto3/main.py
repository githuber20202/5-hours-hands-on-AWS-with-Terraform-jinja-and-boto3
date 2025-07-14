from jinja2 import Template
import random
import string
vpc_id = "vpc-0a691b1cda1dea4be"


suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
# אפשרויות AMI ו-Instance Type
ami_options = {
    "1": "ami-0c995fbcf99222492",  # Ubuntu 24.04 LTS (us-east-2)
    "2": "ami-0915e09cc7ceee3ab"   # Amazon Linux 2023 (us-east-2)
}

instance_types = {
    "1": "t3.small",
    "2": "t3.medium"
}

# קלט מהמשתמש
print("Select AMI:")
print("1. Ubuntu")
print("2. Amazon Linux")
ami_choice = input("Enter your choice (1 or 2): ").strip()

print("Select Instance Type:")
print("1. t3.small")
print("2. t3.medium")
instance_type_choice = input("Enter your choice (1 or 2): ").strip()

region = input("Enter AWS region (only 'us-east-2' is allowed): ").strip()
if region != "us-east-2":
    print("Invalid region. Defaulting to 'us-east-2'")
    region = "us-east-2"

availability_zone = input("Enter availability zone (e.g., us-east-2a): ").strip()
load_balancer_name = input("Enter name for the Load Balancer: ").strip()

# ממפים את הבחירות
ami = ami_options.get(ami_choice, "ami-?????")
instance_type = instance_types.get(instance_type_choice, "t3.small")

# התבנית עצמה (מהמבחן)
terraform_template = """provider "aws" {
  region = "{{ region }}"
}

resource "aws_instance" "web_server" {
  ami = "{{ ami }}"
  instance_type = "{{ instance_type }}"
  availability_zone = "{{ availability_zone }}"
  subnet_id = "subnet-09a9b4fe4e74051b3"
  tags = {
    Name = "WebServer"
  }
}

resource "aws_lb" "application_lb" {
  name               = "{{ load_balancer_name }}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = local.public_subnets
}

resource "aws_security_group" "lb_sg" {
  name        = "lb_security_group_{{ suffix }}"
  description = "Allow HTTP inbound traffic"
  vpc_id      = "{{ vpc_id }}"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.application_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_target_group.arn
  }
}

resource "aws_lb_target_group" "web_target_group" {
  name     = "web-target-group-{{ suffix }}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = "{{ vpc_id }}"
}

resource "aws_lb_target_group_attachment" "web_instance_attachment" {
  target_group_arn = aws_lb_target_group.web_target_group.arn
  target_id        = aws_instance.web_server.id
}

locals {
  public_subnets = ["subnet-09a9b4fe4e74051b3", "subnet-05860172a9327d826"]
}

output "instance_id" {
  value = aws_instance.web_server.id
}

output "instance_public_ip" {
  value = aws_instance.web_server.public_ip
}

output "load_balancer_dns" {
  value = aws_lb.application_lb.dns_name
}

"""

# מרנדרים
template = Template(terraform_template)
rendered_tf = template.render(
    ami=ami,
    instance_type=instance_type,
    region=region,
    availability_zone=availability_zone,
    load_balancer_name=load_balancer_name,
    vpc_id=vpc_id,
    suffix=suffix
)

# שומרים לקובץ
with open("generated.tf", "w") as f:
    f.write(rendered_tf)

print("✅ Terraform file 'generated.tf' created.")

from python_terraform import Terraform
import sys

print("\n🚀 Running Terraform commands...\n")

tf = Terraform(working_dir='.')

try:
    # terraform init
    print("🔧 terraform init:")
    return_code, stdout, stderr = tf.init()
    print(stdout)
    if return_code != 0:
        raise Exception(f"Init failed:\n{stderr}")

    # terraform plan עם שמירה לקובץ
    print("\n🔍 terraform plan:")
    return_code, stdout, stderr = tf.plan(out="tfplan")
    print(stdout)
    print("STDERR:", stderr)
    if return_code != 0:
        raise Exception(f"Plan failed!\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
    print(f"\nℹ️ Plan return code: {return_code}")

    # terraform apply לפי התוכנית tfplan
    print("\n⚙️ terraform apply:")
    return_code, stdout, stderr = tf.apply(plan="tfplan", auto_approve=True)
    print(stdout)
    if return_code != 0:
        raise Exception(f"Apply failed:\n{stderr}")

    print("\n✅ Terraform apply completed successfully.")

    # הוצאת Outputs
    print("\n📤 Fetching Terraform outputs:")
    return_code, stdout, stderr = tf.output()
    print(stdout)

except Exception as e:
    print(f"\n❌ ERROR during Terraform execution:\n{e}")
    sys.exit(1)