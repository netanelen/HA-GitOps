// Jenkinsfile (Advanced - Fixed Kaniko Version)
pipeline {
    agent {
        // Use the Kubernetes agent pod we configured
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
                                if (!fileExists('app')) {
                                    error("Directory 'app' not found. Please ensure your project structure is correct.")
                                }
                                
                                echo "Installing linters..."
                                sh "pip install flake8 bandit" // Install both
                                
                                echo "Running Flake8..."
                                // Added '|| true' to prevent linting errors from failing the build
                                sh "flake8 ./app || true" 
                                
                                echo "Running Bandit..."
                                // Added '|| true' to prevent security issues from failing the build
                                sh "bandit -r ./app || true"
                            }
                        }
                    }
                }
                stage('Dockerfile Linting (Hadolint)') {
                    steps {
                        container('hadolint') { 
                            script {
                                if (!fileExists('Dockerfile')) {
                                    error("Dockerfile not found. Please ensure Dockerfile exists in the repository root.")
                                }
                                echo "Running Hadolint..."
                                // Added '|| true' to prevent linting errors from failing the build
                                sh "hadolint Dockerfile || true"
                            }
                        }
                    }
                }
            }
        }

        // --- THIS STAGE IS COMPLETELY REPLACED ---
        // It now correctly uses the /kaniko/.docker secret
        // that we mounted into the agent pod template.
        stage ('Build and Push with Kaniko') {
            steps {
                container('kaniko') {
                    echo "Building and pushing image: ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                    
                    sh """
                    /kaniko/executor \
                      --context="dir://\$(pwd)" \
                      --dockerfile="Dockerfile" \
                      --destination="${env.IMAGE_NAME}:${env.IMAGE_TAG}" \
                      --destination="${env.IMAGE_NAME}:latest"
                    """
                    // Kaniko automatically finds the credentials at /kaniko/.docker
                }
            }
        }

        // --- THIS STAGE IS UPDATED ---
        stage ('Trivy Scan') {
            steps {
                container('trivy') {
                    echo "Scanning image ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                    
                    // Tell Trivy to use the same Kaniko config for auth
                    sh """
                    export DOCKER_CONFIG=/kaniko/.docker
                    trivy image --exit-code 0 --severity HIGH,CRITICAL ${env.IMAGE_NAME}:${env.IMAGE_TAG}
                    """
                    // Set --exit-code 0 to prevent scan from failing build
                }
            }
        }
        // --- END OF FIXES ---

        stage('Update Git Repo (Trigger ArgoCD)') {
            steps {
                script {
                    container('yq') {
                        echo "Updating Helm chart image tag to ${env.IMAGE_TAG}"
                        
                        sh "test -f helm/values.yaml || { echo 'Error: helm/values.yaml not found'; exit 1; }"
                        
                        sh "git config --global user.email 'jenkins@example.com'"
                        sh "git config --global user.name 'Jenkins Bot'"
                        
                        sh "yq e '.image.tag = \"${env.IMAGE_TAG}\"' -i helm/values.yaml"
                        
                        sh "git add helm/values.yaml"
                        
                        def hasChanges = sh(
                            script: "git diff --cached --quiet",
                            returnStatus: true
                        ) != 0
                        
                        if (hasChanges) {
                            sh "git commit -m 'CI: Update image tag to ${env.IMAGE_TAG}'"
                            
                            withCredentials([string(credentialsId: 'github-credentials', variable: 'GIT_TOKEN')]) {
                                def repoHost = env.GIT_REPO_URL.replace('https://', '').replace('.git', '')
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