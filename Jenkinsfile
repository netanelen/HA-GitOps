// Jenkinsfile (Advanced)
pipeline {
    agent {
        // Use the Kubernetes agent pod we configured and tested
        label 'agent-base'
    }

    environment {
        // Change these to match your repo and Docker Hub username
        DOCKERHUB_USERNAME    = "ste18nati" 
        IMAGE_NAME            = "${DOCKERHUB_USERNAME}/flask-aws-monitor"
        GIT_REPO_URL          = "https://github.com/netanelen/HA-GitOps.git" 
        
        // Use BUILD_NUMBER for unique, traceable image tags
        IMAGE_TAG             = "v${env.BUILD_NUMBER}" 
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        retry(2) 
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: env.GIT_REPO_URL, credentialsId: 'github-credentials'
            }
        }

        stage('Parallel Checks') {
            parallel {
                stage('Python Lint & Scan (Flake8 + Bandit)') {
                    steps {
                        container('python') {
                            script {
                                // Check if app directory exists
                                if (!fileExists('app')) {
                                    error("Directory 'app' not found. Please ensure your project structure is correct.")
                                }
                                
                                echo "Installing linters..."
                                sh "pip install flake8 bandit" // Install both
                                
                                echo "Running Flake8..."
                                sh "flake8 ./app" // Fails pipeline if linting errors found
                                
                                echo "Running Bandit..."
                                sh "bandit -r ./app" // Fails pipeline if security issues found
                            }
                        }
                    }
                }
                stage('Dockerfile Linting (Hadolint)') {
                    steps {
                        container('hadolint') { // This container uses 'sleep infinity'
                            script {
                                if (!fileExists('Dockerfile')) {
                                    error("Dockerfile not found. Please ensure Dockerfile exists in the repository root.")
                                }
                                echo "Running Hadolint..."
                                sh "hadolint Dockerfile" // Fails pipeline if Dockerfile issues found
                            }
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
                        // Use usernamePassword credential type for Docker Hub
                        withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                            sh "echo '${DOCKERHUB_PASS}' | docker login -u '${DOCKERHUB_USER}' --password-stdin"
                            
                            echo "Building Docker image: ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                            sh "docker build -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} ."
                        }
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
                script {
                    container('docker') { // Use the 'docker' container again
                        // Re-authenticate if needed (credentials may have expired)
                        withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                            sh "echo '${DOCKERHUB_PASS}' | docker login -u '${DOCKERHUB_USER}' --password-stdin"
                            
                            echo "Pushing Docker image: ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                            sh "docker push ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                            
                            // Also push a 'latest' tag
                            sh "docker tag ${env.IMAGE_NAME}:${env.IMAGE_TAG} ${env.IMAGE_NAME}:latest"
                            sh "docker push ${env.IMAGE_NAME}:latest"
                        }
                    }
                }
            }
        }

        stage('Update Git Repo (Trigger ArgoCD)') {
            steps {
                script {
                    // Use 'yq' container for a robust YAML edit
                    container('yq') {
                        echo "Updating Helm chart image tag to ${env.IMAGE_TAG}"
                        
                        // Validate that helm/values.yaml exists
                        sh "test -f helm/values.yaml || { echo 'Error: helm/values.yaml not found'; exit 1; }"
                        
                        sh "git config --global user.email 'jenkins@example.com'"
                        sh "git config --global user.name 'Jenkins Bot'"
                        
                        // 'yq' is cleaner and safer than 'sed'
                        sh "yq e '.image.tag = \"${env.IMAGE_TAG}\"' -i helm/values.yaml"
                        
                        sh "git add helm/values.yaml"
                        
                        // Check if there are changes to commit (avoid empty commits)
                        def hasChanges = sh(
                            script: "git diff --cached --quiet",
                            returnStatus: true
                        ) != 0
                        
                        if (hasChanges) {
                            sh "git commit -m 'CI: Update image tag to ${env.IMAGE_TAG}'"
                            
                            // Push using credentials (token will be masked in logs by Jenkins)
                            withCredentials([string(credentialsId: 'github-credentials', variable: 'GIT_TOKEN')]) {
                                def repoHost = env.GIT_REPO_URL.replace('https://', '').replace('.git', '')
                                // Use sh with returnStdout:false to ensure token masking works
                                sh "git push https://${GIT_TOKEN}@${repoHost} HEAD:main"
                            }
                        } else {
                            echo "No changes to commit - image tag may already be ${env.IMAGE_TAG}"
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            echo 'Pipeline finished.'
            // Clean up Docker images to save space
            script {
                try {
                    container('docker') {
                        sh """
                            docker rmi ${env.IMAGE_NAME}:${env.IMAGE_TAG} || true
                            docker rmi ${env.IMAGE_NAME}:latest || true
                            docker system prune -f || true
                        """
                    }
                } catch (Exception e) {
                    echo "Docker cleanup failed: ${e.getMessage()}"
                }
            }
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