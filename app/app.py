import os
import boto3
from flask import Flask, render_template

app = Flask(__name__)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = "us-east-1"

try:
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=REGION
    )
    ec2_client = session.client("ec2")
    elb_client = session.client("elbv2")
except Exception as e:
    print(f"Error initializing Boto3: {e}")
    ec2_client = None
    elb_client = None

@app.route("/")
def home():
    if not ec2_client or not elb_client:
        return "Error: Boto3 clients not initialized. Check AWS credentials.", 500

    try:
        instances = ec2_client.describe_instances()
        instance_data = []
        for reservation in instances["Reservations"]:
            for instance in reservation["Instances"]:
                instance_data.append({
                    "ID": instance["InstanceId"],
                    "State": instance["State"]["Name"],
                    "Type": instance["InstanceType"],
                    "Public IP": instance.get("PublicIpAddress", "N/A")
                })

        
        vpcs = ec2_client.describe_vpcs()
        vpc_data = [{"VPC ID": vpc["VpcId"], "CIDR": vpc["CidrBlock"]} for vpc in vpcs["Vpcs"]]

        
        lbs = elb_client.describe_load_balancers()
        lb_data = [{"LB Name": lb["LoadBalancerName"], "DNS Name": lb["DNSName"]} for lb in lbs["LoadBalancers"]]

        
        amis = ec2_client.describe_images(Owners=['self'])
        ami_data = [{"AMI ID": ami["ImageId"], "Name": ami.get("Name", "N/A")} for ami in amis["Images"]]

    except Exception as e:
        return f"Error fetching AWS data: {e}", 500

    
    return render_template("index.html", 
                           instance_data=instance_data, 
                           vpc_data=vpc_data, 
                           lb_data=lb_data, 
                           ami_data=ami_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)