import boto3
import json
from jinja2 import Template
from python_terraform import Terraform, IsFlagged

    # === EC2 VALIDATION ===
def validate_aws_resources(lb_name="my-lb"):
    print("\n🔍 Validating AWS resources with boto3...")

    ec2 = boto3.resource('ec2')
    client_elb = boto3.client('elbv2')

    # === EC2 VALIDATION ===
    print("🔎 Searching for EC2 instance with tag Name=WebServer...")
    instances = list(ec2.instances.filter(
        Filters=[
            {'Name': 'tag:Name', 'Values': ['WebServer']},
            {'Name': 'instance-state-name', 'Values': ['pending', 'running']}
        ]
    ))

    if not instances:
        print("❌ No EC2 instance found.")
        instance_id = public_ip = instance_state = None
    else:
        instance = instances[0]
        instance.wait_until_running()
        instance.reload()

        instance_id = instance.id
        public_ip = instance.public_ip_address
        instance_state = instance.state['Name']
        print(f"✅ EC2 Instance found: {instance_id} - state: {instance_state}")

    # === LOAD BALANCER VALIDATION ===
    print(f"🔎 Searching for Load Balancer named '{lb_name}'...")
    try:
        response = client_elb.describe_load_balancers(Names=[lb_name])
        lb_dns = response['LoadBalancers'][0]['DNSName']
        print(f"✅ Load Balancer found: {lb_dns}")
    except client_elb.exceptions.LoadBalancerNotFoundException:
        print("❌ Load Balancer not found.")
        lb_dns = None

    # === SAVE TO JSON ===
    data = {
        "instance_id": instance_id,
        "instance_state": instance_state,
        "public_ip": public_ip,
        "load_balancer_dns": lb_dns
    }

    with open("aws_validation.json", "w") as f:
        json.dump(data, f, indent=4)

    print("\n📦 Validation data saved to 'aws_validation.json'.")



def run_terraform():
    print("\n🚀 Running Terraform commands...")

    tf = Terraform(working_dir='.')

    # === INIT ===
    print("🔧 terraform init:")
    return_code, stdout, stderr = tf.init()
    print(stdout)
    if stderr:
        print("\n⚠️ stderr from init:")
        print(stderr)
    if return_code != 0:
        print("❌ terraform init failed!")
        return False

    # === PLAN ===
    print("\n🔎 terraform plan:")
    return_code, stdout, stderr = tf.plan(no_color=IsFlagged)
    print(stdout)

    # הדפסת stderr אם קיים
    if stderr:
        print("\n⚠️ stderr from plan:")
        print(stderr)

    # ניתוח חכם של תוצאה
    if "Error:" in stdout or "Error:" in stderr:
        print("❌ Detected errors in terraform plan output.")
        return False

    if return_code != 0:
        print("⚠️ Non-zero return code from terraform plan, but no error message found.")
        print("🟡 Continuing cautiously...")

    # === APPLY ===
    print("\n🚀 terraform apply:")
    return_code, stdout, stderr = tf.apply(skip_plan=True, capture_output=False, no_color=IsFlagged)
    print(stdout)
    if stderr:
        print("\n⚠️ stderr from apply:")
        print(stderr)
    if return_code != 0:
        print("❌ terraform apply failed!")
        return False

    print("\n✅ Terraform apply completed successfully.")
    return True



def render_template(context, template_path="terraform_template.j2", output_path="generated.tf"):
    try:
        with open(template_path) as file_:
            template = Template(file_.read())

        rendered = template.render(**context)

        with open(output_path, "w") as f:
            f.write(rendered)

        print(f"\n✅ Terraform file '{output_path}' generated successfully.")

    except Exception as e:
        print(f"❌ Error while rendering template: {e}")


# === user_input.py ===
def get_user_input():
    print("🧠 Select AMI:")
    print("1. Ubuntu")
    print("2. Amazon Linux")
    ami_choice = input("Enter your choice (1 or 2): ").strip()

    ami_options = {
        "1": "ami-0c2b8ca1dad447f8a",   # Ubuntu (example)
        "2": "ami-0c94855ba95c71c99"    # Amazon Linux (example)
    }

    ami = ami_options.get(ami_choice)
    if not ami:
        print("⚠️ Invalid AMI choice. Defaulting to Ubuntu.")
        ami = ami_options["1"]
        
        
    print("\n💡 Select Instance Type:")
    print("1. t3.small")
    print("2. t3.medium")
    instance_type_choice = input("Enter your choice (1 or 2): ").strip()

    instance_types = {
        "1": "t3.small",
        "2": "t3.medium"
    }

    instance_type = instance_types.get(instance_type_choice)
    if not instance_type:
        print("⚠️ Invalid instance type. Defaulting to t3.small.")
        instance_type = instance_types["1"]

    region = input("\n🌍 Enter AWS region (only 'us-east-1' allowed): ").strip()
    if region != "us-east-1":
        print("⚠️ Region not allowed. Defaulting to 'us-east-1'.")
        region = "us-east-1"

    az = input("🗺️ Enter availability zone (e.g., us-east-1a): ").strip()
    if not az.startswith(region):
        print("⚠️ Availability Zone doesn't match region. Defaulting to 'us-east-1a'.")
        az = "us-east-1a"

    lb_name = input("🔧 Enter Load Balancer name (e.g., my-lb): ").strip()
    if not lb_name:
        print("⚠️ No name provided. Defaulting to 'my-lb'.")
        lb_name = "my-lb"

    # Return all as dictionary
    return {
        "ami": ami,
        "instance_type": instance_type,
        "region": region,
        "availability_zone": az,
        "load_balancer_name": lb_name
    }
    
# ✅ Runner
if __name__ == "__main__":
    user_inputs = get_user_input()
    print("\n✅ User input collected successfully:\n")
    for key, value in user_inputs.items():
        print(f"{key}: {value}")
        
    render_template(user_inputs)
    
    success = run_terraform()
    if not success:
        print("❌ Terraform execution failed. Exiting.")
        exit(1)
        
    validate_aws_resources(lb_name=user_inputs['load_balancer_name'])