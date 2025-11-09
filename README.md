
## HA-GitOps
## HA-GitOps

## Overview
This project provides a simple Flask web application to monitor AWS resources (EC2 instances, VPCs, Load Balancers, and AMIs) and deploys it using Helm on Kubernetes. It includes CI/CD automation with Jenkins and a Dockerized deployment.

## Architecture

![HA-GitOps architecture](Documents/HA-GitOps.png)

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



---

HA-GitOps: AWS Resource Monitor

📜 Overview
This project demonstrates a complete End-to-End DevOps and GitOps workflow. It features a simple Flask web application designed to monitor AWS resources, which is then containerized with Docker, deployed to Kubernetes using a Helm chart, and fully managed by an advanced Jenkins CI/CD pipeline.

The application provides a simple web interface displaying lists of the following AWS resources:

- Running EC2 Instances

- VPCs

- Load Balancers (ELBv2)

- Available AMIs (owned by the account)

🏛️ Architecture & CI/CD Workflow
This project is built around an automated GitOps workflow. The Jenkinsfile orchestrates the entire process:

1. Git Push: A developer pushes code to the main branch.

2. Jenkins Trigger: The pipeline is automatically triggered.

3. Parallel Checks:

   - Python: Linting (flake8) and security scanning (bandit) run on the app code.

   - Dockerfile: Linting (hadolint) runs on the Dockerfile.

4. Build Image (with Kaniko):

   - A container image is built inside a Kubernetes pod using Kaniko, avoiding Docker-in-Docker.

5. Security Scan (Trivy):

   - The newly built image is scanned for known vulnerabilities (CVEs) using Trivy.

6. Push to Registry:

   - The "clean" image is pushed to Docker Hub with multiple tags (build number, timestamp, and latest).

7. GitOps Update (The Key Step):

   - The pipeline uses yq to automatically update the helm/values.yaml file in the Git repository with the new image tag.

   - This change is committed and pushed back to the main branch.

8. Deployment (ArgoCD):

   - A GitOps tool (like ArgoCD, which is not part of this repo) listening to the repository detects the change in values.yaml and automatically deploys the new version to Kubernetes.

✨ Key Features
Flask Application: A simple boto3-based web app to fetch AWS data.

Multi-stage Dockerfile:

- Clean and efficient build process.

- Uses python:3.9-alpine for a minimal final image.

- Runs as a non-root user (appuser) for enhanced security.

Helm Chart:

- A flexible chart for easy Kubernetes deployment.

- Smart credential management (expects a pre-existing secret named aws-creds).

- Fully configurable via values.yaml.

Advanced Jenkinsfile:

- Contains all modern CI/CD stages (Lint, Scan, Build, Push, Update).

- Uses industry-standard tools (Kaniko, Trivy, Hadolint, Bandit).

🚀 How to Run
Prerequisites
Docker

Kubernetes Cluster (e.g., Minikube, EKS, GKE)

Helm

kubectl

AWS Credentials (Access Key & Secret Key) with read-only access for EC2 and ELB.

1. Local Development
Clone the repository:

```bash
git clone <your-repo-url>
cd HA-GitOps
```
(Recommended) Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```
Install dependencies:

```bash
pip install -r requirements.txt
```
Export your AWS credentials as environment variables:

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
```
Run the app:

```bash
python app/app.py
```
Open your browser to: http://localhost:5001

2. Run with Docker
Build the image:

```bash
docker build -t flask-aws-monitor .
```
Run the container, passing the AWS credentials:

```bash
docker run -p 5001:5001 \
  -e AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY" \
  -e AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY" \
  flask-aws-monitor
```
Open your browser to: http://localhost:5001

3. Deploy to Kubernetes (with Helm)
This is the intended deployment method for this project.

Step 1: Create the AWS Credentials Secret

The deployment expects a Kubernetes secret named aws-creds. Replace the values with your actual keys.

```bash
kubectl create secret generic aws-creds \
  --from-literal=AWS_ACCESS_KEY_ID='YOUR_ACCESS_KEY' \
  --from-literal=AWS_SECRET_ACCESS_KEY='YOUR_SECRET_KEY'
```
Step 2: Update values.yaml (Optional)

If you are using your own image from Docker Hub, update the following line in helm/values.yaml:

```yaml
image:
  repository: ste18nati/flask-aws-monitor # <-- Change to your image repository
  tag: "v64" # The CI/CD pipeline will update this automatically
```
Step 3: Install the Helm Chart

From the project's root directory, run:

```bash
# Install the chart named 'flask-aws-app' from the local 'helm' directory
helm install flask-aws-app ./helm
```
Step 4: Verify the Deployment

Check that the pod is running:

```bash
kubectl get pods
# NAME                               READY   STATUS    RESTARTS   AGE
# flask-aws-app-5f6f8d...            1/1     Running   0          2m
```
Check the service:



