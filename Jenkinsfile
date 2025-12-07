pipeline {
    agent any

    environment {
        // Change this to your real Docker Hub repo
        DOCKER_IMAGE = "yourdockeruser/flexcellent-backend"
    }

    stages {
        stage('Checkout') {
            steps {
                // Uses the repo configured in the job
                checkout scm
            }
        }

        stage('Build & Test') {
            steps {
                sh '''
                python -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                pip install pytest
                pytest
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh """
                docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                """
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',   // 👈 create this in Jenkins
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh """
                    echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin
                    docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    docker push ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        // Later we can add:
        // stage('Deploy to Kubernetes') { ... }
    }

    post {
        always {
            echo "Build finished with status: ${currentBuild.currentResult}"
        }
    }
}
