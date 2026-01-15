pipeline {
    agent any

    environment {
        DOCKER_USER = 'byllkoy259' 
        IMAGE_NAME = 'markdown-pdf-backend'
        
        FULL_IMAGE = "${DOCKER_USER}/${IMAGE_NAME}"
        DOCKER_TAG = "${BUILD_NUMBER}"
        REGISTRY_CRED_ID = 'docker-hub-creds' 
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Đang build image: ${FULL_IMAGE}:${DOCKER_TAG}"
                    sh "docker build -t ${FULL_IMAGE}:${DOCKER_TAG} ."
                    
                    sh "docker tag ${FULL_IMAGE}:${DOCKER_TAG} ${FULL_IMAGE}:latest"
                }
            }
        }

        // Quét bảo mật bằng Trivy
        stage('Scan Vulnerabilities') {
            steps {
                script {
                    echo "Đang quét lỗ hổng bảo mật..."
                    sh "trivy image --severity HIGH,CRITICAL --exit-code 0 ${FULL_IMAGE}:${DOCKER_TAG}"
                }
            }
        }

        // Đẩy lên Docker Hub
        stage('Push to Docker Hub') {
            steps {
                script {
                    echo "Đang đẩy image lên Docker Hub..."
                    withCredentials([usernamePassword(credentialsId: REGISTRY_CRED_ID, passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                        sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                        sh "docker push ${FULL_IMAGE}:${DOCKER_TAG}"
                        sh "docker push ${FULL_IMAGE}:latest"
                    }
                }
            }
        }
    }

    // Dọn dẹp sau khi chạy
    post {
        always {
            sh "docker logout"
            sh "docker rmi ${FULL_IMAGE}:${DOCKER_TAG} || true"
            sh "docker rmi ${FULL_IMAGE}:latest || true"
        }
    }
}