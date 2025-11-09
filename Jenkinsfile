pipeline {
    agent {
        label 'agent-base'
    }

    environment {
        DOCKERHUB_USERNAME    = "ste18nati" 
        IMAGE_NAME            = "${DOCKERHUB_USERNAME}/flask-aws-monitor"
        GIT_REPO_URL          = "https://github.com/netanelen/HA-GitOps.git" 
        IMAGE_TAG             = "v${env.BUILD_NUMBER}"
        TIMESTAMP             = new Date().format('yyyyMMdd-HHmmss')
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        retry(2) 
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'dev', url: env.GIT_REPO_URL, credentialsId: 'github-credentials'
            }
        }

        stage('Parallel Checks') {
            parallel {
                stage('Python Lint & Scan (Flake8 + Bandit)') {
                    steps {
                        container('python') {
                            script {
                                if (!fileExists('app')) {
                                    error("Directory 'app' not found.")
                                }
                                echo "Installing linters..."
                                sh "pip install flake8 bandit" 
                                echo "Running Flake8..."
                                sh "flake8 ./app || true" 
                                echo "Running Bandit..."
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
                                    error("Dockerfile not found.")
                                }
                                echo "Running Hadolint..."
                                sh "hadolint Dockerfile || true"
                            }
                        }
                    }
                }
            }
        }

        stage ('Build and Push with Kaniko') {
            steps {
                container('kaniko') {
                    echo "Building and pushing image with tags: ${env.IMAGE_TAG}, ${env.TIMESTAMP}, and latest"
                    sh """
                    /kaniko/executor \
                      --context="dir://\$(pwd)" \
                      --dockerfile="Dockerfile" \
                      --destination="${env.IMAGE_NAME}:${env.IMAGE_TAG}" \
                      --destination="${env.IMAGE_NAME}:latest" \
                      --destination="${env.IMAGE_NAME}:${env.TIMESTAMP}"
                    """
                }
            }
        }

        stage ('Trivy Scan') {
            steps {
                container('trivy') {
                    echo "Scanning image ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                    sh """
                    export DOCKER_CONFIG=/kaniko/.docker
                    trivy image --exit-code 0 --severity HIGH,CRITICAL ${env.IMAGE_NAME}:${env.IMAGE_TAG}
                    """
                }
            }
        }

        stage('Update Git Repo (Trigger ArgoCD)') {
            steps {
                container('yq') {
                    echo "Updating Helm chart image tag to ${env.IMAGE_TAG}"
                    sh "test -f helm/values.yaml || { echo 'Error: helm/values.yaml not found'; exit 1; }"
                    sh "yq e '.image.tag = \"${env.IMAGE_TAG}\"' -i helm/values.yaml"
                }
                
                echo "Committing and pushing changes..."
                script {
                    sh "git config --global user.email 'jenkins@example.com'"
                    sh "git config --global user.name 'Jenkins Bot'"
                    sh "git add helm/values.yaml"
                    
                    def hasChanges = sh(
                        script: "git diff --cached --quiet",
                        returnStatus: true
                    ) != 0
                    
                    if (hasChanges) {
                        sh "git commit -m 'CI: Update image tag to ${env.IMAGE_TAG}'"
                        
                        withCredentials([usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                            sh "git push https://${GIT_TOKEN}@${env.GIT_REPO_URL.replace('https://', '').replace('.git', '')} HEAD:main"
                        }
                    } else {
                        echo "No changes to commit"
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