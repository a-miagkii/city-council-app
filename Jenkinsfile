pipeline {
  agent any

  environment {
    IMAGE_NAME = "myagky/citycouncil"

    // Параметры stage-сервера:
    STAGE_HOST = "10.211.55.16"     // <-- IP твоего stage
    STAGE_USER = "myagky"             // <-- логин на stage
    STAGE_DIR  = "/home/myagky/city-council-stage"

    // Тег по номеру билда
    BUILD_TAG = "${env.BUILD_NUMBER}"
  }

  options { timestamps() }

  stages {
    stage('Checkout') {
      steps { checkout scm }
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

    stage('Deploy to STAGE') {
      when { branch 'dev' }     // деплоим на stage только из ветки dev
      steps {
        sshagent (credentials: ['stage-server-ssh']) {
          sh '''
            set -eux
            ssh -o StrictHostKeyChecking=no ${STAGE_USER}@${STAGE_HOST} <<'EOF'
              set -eux
              # папка проекта на stage
              mkdir -p ${STAGE_DIR}
              cd ${STAGE_DIR}
              # убедимся, что compose файл на месте (если не скопирован заранее - создадим шаблон один раз)
              if [ ! -f docker-compose.yaml ]; then
                cat > docker-compose.yaml <<'EOC'
version: '3.8'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: cityuser
      POSTGRES_PASSWORD: citypass
      POSTGRES_DB: citycouncil
    volumes:
      - pgdata_stage:/var/lib/postgresql/data
  web:
    image: myagky/citycouncil:latest
    env_file: .env
    depends_on:
      - db
    ports:
      - "8081:8000"
    volumes:
      - ./uploads:/app/static/uploads
volumes:
  pgdata_stage:
EOC
              fi

              # .env должен быть заранее создан вручную (или сгенерируй шаблон на первый запуск)
              if [ ! -f .env ]; then
                cat > .env <<'EOV'
SECRET_KEY=change-me
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://cityuser:citypass@db:5432/citycouncil
FLASK_ENV=production
EOV
              fi

              mkdir -p uploads

              # тянем новый образ и перезапускаем
              docker compose pull web
              docker compose up -d

              # при самом первом запуске можно разово наполнить БД демо-данными:
              # docker compose exec web python seeds.py || true

              docker compose ps
            EOF
          '''
        }
      }
    }
  }

  post {
    success {
      echo "✅ Pushed ${IMAGE_NAME}:${BUILD_TAG} and deployed to STAGE (if dev)."
    }
    failure {
      echo "❌ Pipeline failed"
    }
  }
}

