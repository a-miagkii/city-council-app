pipeline {
    agent any

    environment {
        IMAGE_NAME = "myagky/citycouncil"
        BUILD_TAG  = "${env.BUILD_NUMBER}"
    }

    options {
        timestamps()   // добавляем таймстемпы в логи
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker image') {
            steps {
                sh '''
                  echo "Building Docker image..."
                  docker build -t ${IMAGE_NAME}:${BUILD_TAG} -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_PASS'
                )]) {
                    sh '''
                      echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                      docker push ${IMAGE_NAME}:${BUILD_TAG}
                      docker push ${IMAGE_NAME}:latest
                      docker logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ Image ${IMAGE_NAME}:${BUILD_TAG} and :latest pushed successfully"
        }
        failure {
            echo "❌ Build failed"
        }
    }
}

