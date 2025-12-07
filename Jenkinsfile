pipeline {
    agent any

    environment {
        // Change this to your real Docker Hub repo
        DOCKER_IMAGE = "sassy2711/flexcellent-backend"
    }

    stages {
        stage('Checkout') {
            steps {
                // Uses the repo configured in the jo
                checkout scm
            }
        }

        stage('Build & Test Image') {
            steps {
                sh """
                # 1) Build the image once (Python 3.11 from your Dockerfile)
                docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .

                # 2) Run tests *inside* the built image
                docker run --rm ${DOCKER_IMAGE}:${BUILD_NUMBER} sh -c "pip install pytest && pytest"
                """
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh """
                    # Tag the already-built image as latest
                    docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest

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
