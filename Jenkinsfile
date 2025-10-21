pipeline {
  agent any

  environment {
    IMAGE_NAME = "myagky/citycouncil"
    BUILD_TAG  = "${env.BUILD_NUMBER}"

    STAGE_HOST = "10.211.55.16"
    STAGE_USER = "myagky"
    STAGE_DIR  = "/home/myagky/city-council-stage"
  }

  options { timestamps() }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    // ===== СТАТИКА =====
    stage('Static: Ruff (code quality)') {
      steps {
        sh '''
          set -eux
          docker run --rm \
            -v "$PWD":/repo -w /repo \
            python:3.11-slim bash -lc '
              set -euo pipefail
              pip install --no-cache-dir ruff >/dev/null
              ruff --version

              shopt -s globstar nullglob
              files=(**/*.py *.py)
              if [ ${#files[@]} -eq 0 ]; then
                echo "Ruff: .py файлов не найдено — пропуск."
                exit 0
              fi

              ruff check "${files[@]}"
            '
        '''
      }
    }

    stage('Static: Bandit (security)') {
      steps {
        sh '''
          set -eux
          docker run --rm \
            -v "$PWD":/repo -w /repo \
            python:3.11-slim bash -lc '
              set -euo pipefail
              pip install --no-cache-dir bandit >/dev/null
              bandit --version

              shopt -s globstar nullglob
              files=(**/*.py *.py)
              if [ ${#files[@]} -eq 0 ]; then
                echo "Bandit: .py файлов не найдено — пропуск."
                exit 0
              fi

              bandit -r . -ll -iii
            '
        '''
      }
    }

    stage('Static: Gitleaks (secrets)') {
      steps {
        sh '''
          set -eux
          # если есть локальный конфиг — используем его, иначе запускаем с дефолтами
          if [ -f .gitleaks.toml ]; then
            echo "Gitleaks: найден .gitleaks.toml — используем конфиг"
            docker run --rm -v "$PWD":/repo -w /repo \
              zricethezav/gitleaks:latest \
              detect --no-git --verbose --redact --exit-code 1 -c .gitleaks.toml
          else
            echo "Gitleaks: .gitleaks.toml не найден — запускаем с дефолтной конфигурацией"
            docker run --rm -v "$PWD":/repo -w /repo \
              zricethezav/gitleaks:latest \
              detect --no-git --verbose --redact --exit-code 1
          fi
        '''
      }
    }
    // ===== /СТАТИКА =====

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
          credentialsId: 'dockerhub-creds',   // проверь ID кредов в Jenkins
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
      when { branch 'dev' }  // деплоим только из ветки dev
      steps {
        // проверь ID SSH-кредов; должен совпадать с записью в Jenkins Credentials
        sshagent (credentials: ['stage-server-ssh']) {
          sh """
            set -eux
            ssh -o StrictHostKeyChecking=no ${STAGE_USER}@${STAGE_HOST} \\
              "export STAGE_DIR='${STAGE_DIR}'; export IMAGE_NAME='${IMAGE_NAME}'; bash -s" <<'EOF'
set -eux

mkdir -p "$STAGE_DIR" "$STAGE_DIR/uploads"
cd "$STAGE_DIR"

# docker-compose.yaml — создадим, если нет
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

# .env — создадим, если нет
if [ ! -f .env ]; then
  cat > .env <<'EOV'
SECRET_KEY=change-me
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://cityuser:citypass@db:5432/citycouncil
FLASK_ENV=production
EOV
fi

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
    success { echo "✅ Static checks OK → Build & Push OK → (dev) Deploy OK" }
    failure { echo "❌ Pipeline failed" }
  }
}
