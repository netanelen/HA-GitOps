
# HA-GitOps

## Overview
This project provides a simple Flask web application to monitor AWS resources (EC2 instances, VPCs, Load Balancers, and AMIs) and deploys it using Helm on Kubernetes. It includes CI/CD automation with Jenkins and a Dockerized deployment.

## Features
- View running EC2 instances, VPCs, Load Balancers, and AMIs in your AWS account
- Flask web app with a simple HTML dashboard
- Dockerfile for containerization
- Helm chart for Kubernetes deployment
- Jenkinsfile for CI/CD pipeline

## Prerequisites
- Python 3.9+
- AWS credentials with read access
- Docker
- Kubernetes cluster (for deployment)
- Helm

## Quick Start

1. **Install dependencies:**
	```sh
	pip install -r requirements.txt
	```

2. **Set AWS credentials:**
	Export your AWS credentials as environment variables:
	```sh
	export AWS_ACCESS_KEY_ID=your_access_key
	export AWS_SECRET_ACCESS_KEY=your_secret_key
	```

3. **Run locally:**
	```sh
	python app/app.py
	```
	The app will be available at http://localhost:5001

4. **Build Docker image:**
	```sh
	docker build -t flask-aws-monitor .
	```

5. **Deploy with Helm:**
	- Update `helm/values.yaml` with your image repository and tag.
	- Create a Kubernetes secret named `aws-creds` with your AWS credentials.
	- Install the chart:
	  ```sh
	  helm install flask-aws-monitor ./helm
	  ```

## Project Structure
- `app/` - Flask application code
- `helm/` - Helm chart for Kubernetes deployment
- `Dockerfile` - Container build instructions
- `Jenkinsfile` - CI/CD pipeline definition
- `requirements.txt` - Python dependencies



