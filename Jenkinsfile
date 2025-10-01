pipeline {
  agent any

  environment {
    // Имя образа в Docker Hub
    IMAGE_NAME = "myagky/citycouncil"
    // Тег по номеру сборки
    BUILD_TAG  = "${env.BUILD_NUMBER}"

    // Параметры STAGE-сервера
    STAGE_HOST = "10.211.55.16"                 // <-- IP/хост stage
    STAGE_USER = "myagky"                       // <-- пользователь на stage
    STAGE_DIR  = "/home/myagky/city-council-stage" // <-- каталог с compose на stage
  }

  options { timestamps() }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build Docker image') {
      steps {
        sh """
          echo "Building Docker image..."
          docker build -t ${IMAGE_NAME}:${BUILD_TAG} -t ${IMAGE_NAME}:latest .
        """
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub-creds',   // <- креды Docker Hub (username+token RW)
          usernameVariable: 'DH_USER',
          passwordVariable: 'DH_PASS'
        )]) {
          sh """
            echo "\$DH_PASS" | docker login -u "\$DH_USER" --password-stdin
            docker push ${IMAGE_NAME}:${BUILD_TAG}
            docker push ${IMAGE_NAME}:latest
            docker logout
          """
        }
      }
    }

    stage('Deploy to STAGE') {
      // Для multibranch: деплоим только из ветки dev
      when { branch 'dev' }
      steps {
        // ВАЖНО: тут укажи ID SSH-кредов Jenkins. По логам у тебя это 'myagky'
        sshagent (credentials: ['stage-server-ssh']) {
          sh """
            set -eux

            # Передаём переменные окружения в удалённую сессию и запускаем скрипт без локальной подстановки
            ssh -o StrictHostKeyChecking=no ${STAGE_USER}@${STAGE_HOST} \\
              "export STAGE_DIR='${STAGE_DIR}'; export IMAGE_NAME='${IMAGE_NAME}'; bash -s" <<'EOF'
set -eux

# Подготовим каталог и перейдём в него
mkdir -p "$STAGE_DIR" "$STAGE_DIR/uploads"
cd "$STAGE_DIR"

# Создадим docker-compose.yaml, если его ещё нет (сырой here-doc оставляет текст как есть)
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

# Создадим .env, если отсутствует (для быстрого старта; в проде лучше хранить секреты отдельно)
if [ ! -f .env ]; then
  cat > .env <<'EOV'
SECRET_KEY=change-me
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://cityuser:citypass@db:5432/citycouncil
FLASK_ENV=production
EOV
fi

# Тянем свежий образ и пересоздаём web, чтобы точно применились изменения
docker compose pull web
docker compose up -d --force-recreate web

docker compose ps
EOF
          """
        }
      }
    }
  }

  post {
    success {
      echo "✅ Build & push OK. Deploy to STAGE (для dev) — OK."
    }
    failure {
      echo "❌ Pipeline failed"
    }
  }
}
