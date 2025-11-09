# HA-GitOps: AWS Resource Monitor

A Flask-based web application for monitoring AWS resources (EC2 instances, VPCs, Load Balancers, and AMIs) with a complete GitOps CI/CD pipeline using Jenkins, Docker, Kubernetes, and Helm.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

This project demonstrates a complete **End-to-End DevOps and GitOps workflow**. It features a Flask web application that monitors AWS resources, which is containerized with Docker, deployed to Kubernetes using Helm, and fully automated through a Jenkins CI/CD pipeline.

The application provides a web interface displaying:
- **EC2 Instances** - Running instances with their state, type, and public IPs
- **VPCs** - Virtual Private Clouds with their CIDR blocks
- **Load Balancers** - ELBv2 load balancers with DNS names
- **AMIs** - Amazon Machine Images owned by the account

![HA-GitOps Architecture](Documents/HA-GitOps.png)

## ✨ Features

- **Flask Web Application** - Simple boto3-based web app to fetch and display AWS data
- **Multi-stage Dockerfile** - Optimized container build with minimal Alpine-based image
- **Security Best Practices** - Runs as non-root user, security scanning with Trivy and Bandit
- **Helm Chart** - Flexible Kubernetes deployment with configurable values
- **GitOps Workflow** - Automated CI/CD pipeline that updates Helm values and triggers deployments
- **Code Quality** - Automated linting with Flake8, Hadolint, and security scanning

## 🏛️ Architecture

This project implements a **GitOps workflow** where:

1. Code changes trigger the Jenkins pipeline
2. The pipeline builds, tests, and scans the application
3. A new container image is built and pushed to Docker Hub
4. The Helm chart values are automatically updated in Git
5. ArgoCD (or similar GitOps tool) detects the change and deploys to Kubernetes

### CI/CD Pipeline Stages

The Jenkins pipeline includes the following stages:

1. **Clone Repository** - Checks out the code from Git
2. **Parallel Quality Checks**:
   - Python linting (Flake8) and security scanning (Bandit)
   - Dockerfile linting (Hadolint)
3. **Build & Push** - Builds container image with Kaniko and pushes to Docker Hub
4. **Security Scan** - Scans image for vulnerabilities with Trivy
5. **GitOps Update** - Updates `helm/values.yaml` with new image tag and commits back to Git

## 📦 Prerequisites

- **Python 3.9+** - For local development
- **Docker** - For containerization
- **Kubernetes Cluster** - For deployment (Minikube, EKS, GKE, etc.)
- **Helm 3.x** - For Kubernetes deployment
- **kubectl** - Kubernetes command-line tool
- **AWS Credentials** - Access Key and Secret Key with read-only access to:
  - EC2 (describe instances, VPCs, images)
  - ELBv2 (describe load balancers)
- **Jenkins** - With Kubernetes plugin and required containers (Kaniko, Trivy, Hadolint, Python, yq)

## 🚀 Quick Start

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/netanelen/HA-GitOps.git
   cd HA-GitOps
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set AWS credentials:**
   ```bash
   export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
   export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
   ```

5. **Run the application:**
   ```bash
   python app/app.py
   ```

6. **Access the application:**
   Open your browser to [http://localhost:5001](http://localhost:5001)

### Docker Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t flask-aws-monitor .
   ```

2. **Run the container:**
   ```bash
   docker run -p 5001:5001 \
     -e AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY" \
     -e AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY" \
     flask-aws-monitor
   ```

3. **Access the application:**
   Open your browser to [http://localhost:5001](http://localhost:5001)

## 🔄 CI/CD Pipeline

The Jenkins pipeline automates the entire build, test, and deployment process:

### Pipeline Workflow

```
Git Push → Jenkins Trigger → Parallel Checks → Build Image → Security Scan → Update Git → ArgoCD Deploys
```

### Pipeline Stages Details

1. **Clone Repository** - Checks out code from the main branch
2. **Parallel Checks**:
   - **Python Lint & Scan**: Runs Flake8 for code quality and Bandit for security
   - **Dockerfile Linting**: Runs Hadolint to check Dockerfile best practices
3. **Build and Push with Kaniko**:
   - Builds container image without Docker-in-Docker
   - Tags image with: `v{BUILD_NUMBER}`, `latest`, and `{TIMESTAMP}`
   - Pushes to Docker Hub
4. **Trivy Scan** - Scans the built image for known CVEs
5. **Update Git Repo**:
   - Updates `helm/values.yaml` with the new image tag using `yq`
   - Commits and pushes changes back to trigger ArgoCD

### Jenkins Configuration

The pipeline requires the following Jenkins setup:
- Kubernetes plugin configured
- Container images available: `kaniko`, `trivy`, `hadolint`, `python`, `yq`
- Credentials configured:
  - `github-credentials` - For Git operations
  - Docker Hub credentials (configured in Kaniko)

## 🚢 Deployment

### Kubernetes Deployment with Helm

This is the recommended deployment method for production.

#### Step 1: Create AWS Credentials Secret

The deployment expects a Kubernetes secret named `aws-creds`:

```bash
kubectl create secret generic aws-creds \
  --from-literal=AWS_ACCESS_KEY_ID='YOUR_ACCESS_KEY' \
  --from-literal=AWS_SECRET_ACCESS_KEY='YOUR_SECRET_KEY' \
  --namespace=default  # Or your target namespace
```

#### Step 2: Update Helm Values (Optional)

If using your own Docker Hub image, update `helm/values.yaml`:

```yaml
image:
  repository: your-dockerhub-username/flask-aws-monitor
  tag: "v1"  # CI/CD pipeline will update this automatically
  pullPolicy: Always
```

#### Step 3: Install the Helm Chart

```bash
helm install flask-aws-app ./helm
```

Or with a custom namespace:

```bash
helm install flask-aws-app ./helm --namespace production --create-namespace
```

#### Step 4: Verify the Deployment

Check that the pod is running:

```bash
kubectl get pods
# NAME                               READY   STATUS    RESTARTS   AGE
# flask-aws-app-5f6f8d...            1/1     Running   0          2m
```

Check the service:

```bash
kubectl get svc
# NAME              TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)          AGE
# flask-aws-app     LoadBalancer   10.96.xxx.xxx   <pending>       5001:3xxxx/TCP   2m
```

Get the service URL:

```bash
kubectl get svc flask-aws-app -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

#### Step 5: View Logs

```bash
kubectl logs -f deployment/flask-aws-app
```

### Upgrading the Deployment

```bash
helm upgrade flask-aws-app ./helm
```

### Uninstalling

```bash
helm uninstall flask-aws-app
```

## 📁 Project Structure

```
HA-GitOps/
├── app/
│   ├── app.py              # Flask application
│   └── templates/
│       └── index.html      # Web dashboard template
├── helm/
│   ├── Chart.yaml          # Helm chart metadata
│   ├── values.yaml         # Helm chart values (auto-updated by CI/CD)
│   └── templates/
│       ├── deployment.yaml # Kubernetes deployment
│       └── service.yaml    # Kubernetes service
├── Documents/
│   ├── HA-GitOps.png       # Architecture diagram
│   └── APP-UI.png          # Application UI screenshot
├── Dockerfile              # Multi-stage container build
├── Jenkinsfile             # CI/CD pipeline definition
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## ⚙️ Configuration

### Helm Chart Values

Key configuration options in `helm/values.yaml`:

```yaml
replicaCount: 1              # Number of pod replicas

image:
  repository: ste18nati/flask-aws-monitor
  tag: "#v1"                 # Auto-updated by CI/CD
  pullPolicy: Always

resources:
  limits:
    cpu: "500m"
    memory: "128Mi"
  requests:
    cpu: "250m"
    memory: "64Mi"

service:
  type: LoadBalancer         # Or ClusterIP, NodePort
  port: 5001

ingress:
  enabled: false             # Enable for ingress controller
```

### Environment Variables

The application uses the following environment variables:
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_REGION` - AWS region (defaults to `us-east-1`)

## 🔧 Troubleshooting

### Application Issues

**Error: "Boto3 clients not initialized"**
- Verify AWS credentials are correctly set in the Kubernetes secret
- Check that the secret name matches `aws-creds`
- Ensure credentials have the required permissions

**Error: "Error fetching AWS data"**
- Verify AWS credentials have read access to EC2 and ELBv2
- Check network connectivity from the pod to AWS
- Review pod logs: `kubectl logs <pod-name>`

### Deployment Issues

**Pod not starting:**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**Service not accessible:**
- Check service type (LoadBalancer may take time to provision)
- Verify service selector matches deployment labels
- Check firewall/security group rules

### CI/CD Pipeline Issues

**Pipeline fails at linting:**
- Review linting output in Jenkins console
- Fix code style issues reported by Flake8
- Address security issues reported by Bandit

**Image push fails:**
- Verify Docker Hub credentials in Jenkins
- Check network connectivity from Jenkins agent
- Verify image name and tag format

**Git update fails:**
- Verify GitHub credentials in Jenkins
- Check branch permissions
- Ensure `yq` is available in the container

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Ensure code passes linting (`flake8 app/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused

## 📝 License

This project is provided as-is for educational and demonstration purposes.

## 🔗 Related Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)

---

**Note**: This project is designed for demonstration purposes. For production use, consider:
- Implementing proper authentication and authorization
- Adding rate limiting and request validation
- Using AWS IAM roles instead of access keys
- Implementing proper logging and monitoring
- Adding health checks and readiness probes
- Setting up proper backup and disaster recovery procedures
