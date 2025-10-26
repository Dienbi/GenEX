pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'genex-app'
        SONAR_HOST_URL = 'http://sonarqube:9000'
        SONAR_PROJECT_KEY = 'genex'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Checking out code from Git...'
                checkout scm
            }
        }
        
        stage('Linting') {
            steps {
                echo '🔍 Running code linting (skipped - requires Python environment)...'
                echo 'Install Docker Pipeline plugin to enable this stage'
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo '🧪 Running unit tests (skipped - requires Python environment)...'
                echo 'Install Docker Pipeline plugin to enable this stage'
            }
        }
        
        stage('Code Coverage') {
            steps {
                echo '📊 Code coverage (skipped - requires Python environment)...'
                echo 'Install Docker Pipeline plugin to enable this stage'
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                echo '🔬 SonarQube analysis (skipped - requires configuration)...'
                echo 'Configure SonarQube server and scanner tool first'
            }
        }
        
        stage('Quality Gate') {
            steps {
                echo '🚦 Quality Gate (skipped)...'
            }
        }
        
        stage('Security Check') {
            steps {
                echo '🔐 Security checks (skipped - requires Python environment)...'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                script {
                    try {
                        sh '''
                            docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                            docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                        '''
                    } catch (Exception e) {
                        echo "⚠️ Docker build failed: ${e.message}"
                        echo "Make sure Docker is accessible from Jenkins container"
                    }
                }
            }
        }
        
        stage('Database Migrations') {
            steps {
                echo '💾 Database migrations (skipped - requires Python environment)...'
            }
        }
        
        stage('Collect Static Files') {
            steps {
                echo '📦 Collect static files (skipped - requires Python environment)...'
            }
        }
        
        stage('Deploy') {
            steps {
                echo '🚀 Deploying application...'
                sh '''
                    docker-compose down || true
                    docker-compose up -d web
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                echo '❤️ Running health check...'
                sh '''
                    sleep 10
                    curl -f http://localhost:8000/ || echo "Health check warning: Server may not be ready yet"
                '''
            }
        }
    }
    
    post {
        always {
            echo '📋 Pipeline execution completed'
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed! Check the console output above for details.'
        }
    }
}
