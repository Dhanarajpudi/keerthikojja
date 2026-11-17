pipeline {
  agent any
  environment {
    IMAGE_NAME = 'it-service-desk'
    CONTAINER_NAME = 'it-service-desk-test'
    APP_PORT = '5000'
  }
  stages {
    stage('Checkout') { steps { checkout scm; sh 'git --version' } }
    stage('Automated Tests') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --no-cache-dir -r requirements.txt
          python -m unittest discover -s tests -v
        '''
      }
    }
    stage('Build Image') {
      steps { sh 'docker build --pull -t ${IMAGE_NAME}:${BUILD_NUMBER} .' }
    }
    stage('Smoke Test') {
      steps {
        sh '''
          docker rm -f it-service-desk-smoke >/dev/null 2>&1 || true
          docker run -d --name it-service-desk-smoke -p 5001:5000 ${IMAGE_NAME}:${BUILD_NUMBER}
          for i in $(seq 1 20); do
            curl -fsS http://127.0.0.1:5001/health && break
            sleep 2
          done
          curl -fsS http://127.0.0.1:5001/health
          docker rm -f it-service-desk-smoke
        '''
      }
    }
    stage('Tag Artifact') {
      steps { sh 'docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest && docker image ls ${IMAGE_NAME}' }
    }
    stage('Deploy to Test') {
      steps {
        sh '''
          docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true
          docker run -d --name ${CONTAINER_NAME} --restart unless-stopped \
            -p ${APP_PORT}:5000 -e DB_PATH=/app/data/tickets.db \
            -v /opt/it-service-desk/data:/app/data ${IMAGE_NAME}:${BUILD_NUMBER}
          sleep 5
          curl -fsS http://127.0.0.1:${APP_PORT}/health
          docker ps --filter name=${CONTAINER_NAME}
        '''
      }
    }
  }
  post {
    always { sh 'docker logs it-service-desk-test --tail 50 2>/dev/null || true' }
    success { echo 'IT Service Desk deployed successfully to test.' }
    failure { echo 'Pipeline failed. Inspect stage output and container logs.' }
  }
}
