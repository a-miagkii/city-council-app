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

    // ===== Статика =====
    stage('Static: Ruff (code quality)') {
      steps {
        sh '''
          docker run --rm -v "$PWD":/src ghcr.io/astral-sh/ruff:latest check /src
        '''
      }
    }

    stage('Static: Bandit (security)') {
      steps {
        sh '''
          set -eu
          docker run --rm -v "$PWD":/repo -w /repo python:3.11-slim bash -lc '
            set -euo pipefail
            for i in 1 2 3; do
              if pip install --no-cache-dir bandit >/dev/null; then break; fi
              echo "pip install bandit failed, retry $i/3"; sleep 5
            done
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
          # Проверку наличия конфига делаем внутри контейнера.
          docker run --rm \
            --entrypoint /bin/sh \
            -v "$PWD":/repo -w /repo \
            zricethezav/gitleaks:latest -lc '
              set -eu
              if [ -f .gitleaks.toml ]; then
                echo "Gitleaks: найден .gitleaks.toml — используем конфиг"
                exec gitleaks detect --no-git --verbose --redact --exit-code 1 -c .gitleaks.toml
              else
                echo "Gitleaks: конфиг не найден — используем дефолтные правила"
                exec gitleaks detect --no-git --verbose --redact --exit-code 1
              fi
            '
        '''
      }
    }
    // ===== /Статика =====

    stage('Build Docker image') {
      steps {
        sh '''
          echo "Building Docker image..."
          docker build -t '"${IMAGE_NAME}"':'"${BUILD_TAG}"' -t '"${IMAGE_NAME}"':latest .
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
            docker push '"${IMAGE_NAME}"':'"${BUILD_TAG}"'
            docker push '"${IMAGE_NAME}"':latest
            docker logout
          '''
        }
      }
    }

    stage('Deploy to STAGE') {
      when { branch 'dev' }  // multibranch: деплоим только для dev
      steps {
        sshagent (credentials: ['stage-server-ssh']) {
          sh '''
            set -eu
            ssh -o StrictHostKeyChecking=no '"${STAGE_USER}"'@'"${STAGE_HOST}"' "bash -s" <<'EOF'
set -euo pipefail
export STAGE_DIR='"${STAGE_DIR}"'
export IMAGE_NAME='"${IMAGE_NAME}"'

mkdir -p "$STAGE_DIR" "$STAGE_DIR/uploads"
cd "$STAGE_DIR"

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
    image: '"${IMAGE_NAME}"':latest
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
          '''
        }
      }
    }
  }

  post {
    success { echo "✅ Static checks OK → Build & Push OK → (dev) Deploy OK" }
    failure { echo "❌ Pipeline failed" }
  }
}
