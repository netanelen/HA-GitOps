// Jenkinsfile (Advanced)
pipeline {
    agent {
        // Use the Kubernetes agent pod we configured and tested
        label 'agent-base'
    }

    environment {
        // Use the credentials IDs you created in Jenkins
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials') 
        GIT_CREDENTIALS       = credentials('github-credentials')
        
        // Change these to match your repo and Docker Hub username
        DOCKERHUB_USERNAME    = "YOUR_DOCKERHUB_USERNAME" // Set your username here
        IMAGE_NAME            = "${DOCKERHUB_USERNAME}/flask-aws-monitor"
        GIT_REPO_URL          = "https://github.com/YOUR_USERNAME/YOUR_REPO.git" // Set your repo URL here
        
        // Use BUILD_NUMBER for unique, traceable image tags
        IMAGE_TAG             = "v${env.BUILD_NUMBER}" 
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: env.GIT_REPO_URL
            }
        }

        stage('Parallel Checks') {
            parallel {
                stage('Python Lint & Scan (Flake8 + Bandit)') {
                    steps {
                        container('python') {
                            echo "Installing linters..."
                            sh "pip install flake8 bandit" // Install both
                            
                            echo "Running Flake8..."
                            sh "flake8 ./app"
                            
                            echo "Running Bandit..."
                            sh "bandit -r ./app" // Run bandit here
                        }
                    }
                }
                stage('Dockerfile Linting (Hadolint)') {
                    steps {
                        container('hadolint') { // This container uses 'sleep infinity'
                            echo "Running Hadolint..."
                            sh "hadolint Dockerfile"
                        }
                    }
                }
            }
        }

        stage ('Build & Scan') {
            steps {
                script {
                    // Use the 'docker' container (with the mounted socket) for build and login
                    container('docker') {
                        echo 'Logging in to Docker Hub...'
                        // Use the DOCKERHUB_TOKEN variable from withCredentials
                        withCredentials([string(credentialsId: 'DOCKERHUB_CREDENTIALS', variable: 'DOCKERHUB_TOKEN')]) {
                            sh "docker login -u ${env.DOCKERHUB_USERNAME} -p ${DOCKERHUB_TOKEN}"
                        }
                        
                        echo "Building Docker image: ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                        sh "docker build -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} ."
                    }
                    
                    // Now, use the 'trivy' container to scan the image we just built
                    container('trivy') {
                        echo "Scanning image ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                        // Scan for HIGH,CRITICAL vulnerabilities. Fails pipeline if found.
                        sh "trivy image --exit-code 1 --severity HIGH,CRITICAL ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                container('docker') { // Use the 'docker' container again
                    echo "Pushing Docker image: ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                    sh "docker push ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                    
                    // Also push a 'latest' tag
                    sh "docker tag ${env.IMAGE_NAME}:${env.IMAGE_TAG} ${env.IMAGE_NAME}:latest"
                    sh "docker push ${env.IMAGE_NAME}:latest"
                }
            }
        }

        stage('Update Git Repo (Trigger ArgoCD)') {
            steps {
                // Use 'yq' container for a robust YAML edit
                container('yq') {
                    echo "Updating Helm chart image tag to ${env.IMAGE_TAG}"
                    
                    sh "git config --global user.email 'jenkins@example.com'"
                    sh "git config --global user.name 'Jenkins Bot'"
                    
                    // 'yq' is cleaner and safer than 'sed'
                    sh "yq e '.image.tag = \"${env.IMAGE_TAG}\"' -i helm/values.yaml"
                    
                    sh "git add helm/values.yaml"
                    sh "git commit -m 'CI: Update image tag to ${env.IMAGE_TAG}'"
                    
                    withCredentials([string(credentialsId: 'GIT_CREDENTIALS', variable: 'GIT_TOKEN')]) {
                        // We must strip 'https://' and use the token in the URL
                        def repoHost = env.GIT_REPO_URL.split('//')[1]
                        sh "git push https://${GIT_TOKEN}@${repoHost} HEAD:main"
                    }
                }
            }
        }
    }
     post {
        always {
            echo 'Pipeline finished.'
            // Clean up the workspace
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Check logs for details.'
        }
    }
}