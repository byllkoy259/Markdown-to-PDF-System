pipeline {
    agent any

    environment {
        DOCKER_USER = 'byllkoy259' 
        IMAGE_NAME = 'markdown-pdf-backend'
        FULL_IMAGE = "${DOCKER_USER}/${IMAGE_NAME}"
        DOCKER_TAG = "${BUILD_NUMBER}"
        REGISTRY_CRED_ID = 'docker-hub-creds' 

        POSTGRES_USER = 'baoden'
        POSTGRES_DB = 'markdown_db'
        MINIO_ROOT_USER = 'minioadmin'
        MINIO_BUCKET_NAME = 'pdf-reports'
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

        stage('Scan Vulnerabilities') {
            steps {
                script {
                    echo "Đang quét lỗ hổng bảo mật..."
                    sh "trivy image --severity HIGH,CRITICAL --exit-code 0 ${FULL_IMAGE}:${DOCKER_TAG}"
                }
            }
        }

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

        stage('Deploy to Production') {
            steps {
                script {
                    echo "Đang triển khai phiên bản: ${DOCKER_TAG}"
                    withCredentials([
                        string(credentialsId: 'prod-postgres-password', variable: 'DB_PASS'),
                        string(credentialsId: 'prod-minio-password', variable: 'MINIO_PASS')
                    ]) {
                        sh """
                            echo "POSTGRES_USER=${POSTGRES_USER}" > .env
                            echo "POSTGRES_PASSWORD=${DB_PASS}" >> .env
                            echo "POSTGRES_DB=${POSTGRES_DB}" >> .env
                            echo "MINIO_ROOT_USER=${MINIO_ROOT_USER}" >> .env
                            echo "MINIO_ROOT_PASSWORD=${MINIO_PASS}" >> .env
                            echo "MINIO_BUCKET_NAME=${MINIO_BUCKET_NAME}" >> .env
                            echo "FULL_IMAGE=${FULL_IMAGE}" >> .env
                            echo "DOCKER_TAG=${DOCKER_TAG}" >> .env
                        """
                    }
                    
                    sh "ls -la .env"

                    sh "docker-compose -f docker-compose.prod.yml down || true"
                    sh "docker-compose -f docker-compose.prod.yml up -d"
                    
                    sh "rm .env"
                    
                    sh "docker image prune -f"
                }
            }
        }
    }

    post {
        always {
            sh "docker logout"
            sh "docker rmi ${FULL_IMAGE}:${DOCKER_TAG} || true"
            sh "docker rmi ${FULL_IMAGE}:latest || true"
        }
    }
}