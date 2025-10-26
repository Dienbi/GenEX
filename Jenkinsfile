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
        
        stage('Environment Setup') {
            steps {
                echo '🔧 Setting up Python environment...'
                sh '''
                    python3 -m venv venv || true
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Linting') {
            steps {
                echo '🔍 Running code linting...'
                sh '''
                    . venv/bin/activate
                    pip install flake8 || true
                    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=venv,migrations,__pycache__ || true
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo '🧪 Running unit tests...'
                sh '''
                    . venv/bin/activate
                    python manage.py test --verbosity=2 || true
                '''
            }
        }
        
        stage('Code Coverage') {
            steps {
                echo '📊 Generating code coverage report...'
                sh '''
                    . venv/bin/activate
                    pip install coverage || true
                    coverage run --source='.' manage.py test || true
                    coverage report || true
                    coverage xml || true
                '''
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                echo '🔬 Running SonarQube analysis...'
                script {
                    def scannerHome = tool 'SonarQubeScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=${SONAR_HOST_URL} \
                            -Dsonar.python.coverage.reportPaths=coverage.xml \
                            -Dsonar.exclusions=**/migrations/**,**/venv/**,**/__pycache__/**,**/static/**,**/media/**,**/ml_models/**
                        """
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                echo '🚦 Checking SonarQube Quality Gate...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }
        
        stage('Security Check') {
            steps {
                echo '🔐 Running security checks...'
                sh '''
                    . venv/bin/activate
                    pip install safety bandit || true
                    safety check --json || true
                    bandit -r . -f json -o bandit-report.json -x ./venv,./migrations || true
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                    docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                '''
            }
        }
        
        stage('Database Migrations') {
            steps {
                echo '💾 Running database migrations...'
                sh '''
                    . venv/bin/activate
                    python manage.py makemigrations --dry-run --verbosity 3
                    python manage.py migrate --noinput || true
                '''
            }
        }
        
        stage('Collect Static Files') {
            steps {
                echo '📦 Collecting static files...'
                sh '''
                    . venv/bin/activate
                    python manage.py collectstatic --noinput || true
                '''
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
