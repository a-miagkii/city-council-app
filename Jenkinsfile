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

    // ---------- STATIC CHECKS ----------
    stage('Static: Ruff (code quality)') {
      steps {
        sh(script: '''
          docker run --rm -v "$PWD":/src ghcr.io/astral-sh/ruff:latest check /src
        ''', shell: '/bin/bash')
      }
    }

    stage('Static: Bandit (security)') {
      steps {
        sh '''
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
          docker run --rm --entrypoint /bin/sh \
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
    // ---------- /STATIC CHECKS ----------

    stage('Tests: Pytest') {
      steps {
        sh '''
          docker run --rm \
            -e GIT_BRANCH="${GIT_BRANCH:-}" \
            -e GIT_COMMIT="${GIT_COMMIT:-}" \
            -v "$PWD":/repo -w /repo python:3.11-slim bash -lc '
            set -euo pipefail

            # 1) Виртуалка для тестов
            python -m venv /tmp/venv
            . /tmp/venv/bin/activate

            # 2) Зависимости: если есть requirements.txt — ставим его,
            #    иначе — минимальный набор для запуска тестов
            if [ -f requirements.txt ]; then
              pip install --no-cache-dir -r requirements.txt
            else
              pip install --no-cache-dir pytest pytest-flask pytest-cov coverage
            fi

            # 3) Динамически формируем список пакетов/каталогов для покрытия
            COVARGS=()
            for d in app blueprints models src flask_city_council; do
              if [ -d "$d" ]; then COVARGS+=(--cov="$d"); fi
            done

            PYTEST_ARGS=("--maxfail=1" "--disable-warnings")
            if [ ${#COVARGS[@]} -gt 0 ]; then
              PYTEST_ARGS+=("${COVARGS[@]}")
            fi

            # 5) PYTHONPATH, чтобы импорты из подкаталогов находились
            export PYTHONPATH="${PYTHONPATH:-}:/repo:/repo/src:/repo/flask_city_council"

            # 6) Запуск тестов с покрытием (по возможности)
            #    Если tests/ есть — используем его как цель, иначе пустим pytest по умолчанию.
            TARGET="tests"
            [ -d tests ] || TARGET="."
            PYTEST_ARGS+=("--cov-report=term-missing" "$TARGET")

            set +e
            pytest "${PYTEST_ARGS[@]}"
            RC=$?
            set -e

            case "$RC" in
              0|5)
                :
                ;;
              *)
                exit "$RC"
                ;;
            esac
          '
        '''
      }
    }

    stage('Build Docker image') {
      steps {
        sh '''
          set -eu
          echo "Building Docker image: ${IMAGE_NAME}:${BUILD_TAG}"
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
            set -eu
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker push ${IMAGE_NAME}:${BUILD_TAG}
            docker push ${IMAGE_NAME}:latest
            docker logout
          '''
        }
      }
    }

    stage('Deploy to STAGE') {
      when { branch 'dev' } // деплоим только из dev
      steps {
        sshagent (credentials: ['stage-server-ssh']) {
          // 1) Передаём собранный образ на STAGE и загружаем локально (без pull из Registry)
          sh '''
            set -eu
            echo "Streaming image ${IMAGE_NAME}:${BUILD_TAG} to ${STAGE_USER}@${STAGE_HOST} ..."
            docker save ${IMAGE_NAME}:${BUILD_TAG} | gzip | \
              ssh -o StrictHostKeyChecking=no ${STAGE_USER}@${STAGE_HOST} 'gunzip | docker load'
          '''

          // 2) Обновляем compose и поднимаем web на STAGE с только что загруженным тегом
          sh """
            set -eu
            ssh -o StrictHostKeyChecking=no ${STAGE_USER}@${STAGE_HOST} "bash -s" <<'EOF'
set -euo pipefail
export STAGE_DIR='${STAGE_DIR}'
export IMAGE_NAME='${IMAGE_NAME}'
export BUILD_TAG='${BUILD_TAG}'

mkdir -p "$STAGE_DIR" "$STAGE_DIR/uploads"
cd "$STAGE_DIR"

cat > docker-compose.yaml <<EOC
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
    image: \${IMAGE_NAME}:\${BUILD_TAG}
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

if [ ! -f .env ]; then
  cat > .env <<'EOV'
SECRET_KEY=change-me
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://cityuser:citypass@db:5432/citycouncil
FLASK_ENV=production
EOV
fi

docker compose up -d --force-recreate web
docker compose ps
EOF
          """
        }
      }
    }
  }

  post {
    success { echo "✅ Static OK → Tests OK → Build & Push OK → (dev) Deploy OK" }
    failure { echo "❌ Pipeline failed" }
  }
}
