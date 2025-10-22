pipeline {
  agent any

  environment {
    IMAGE_NAME = "myagky/citycouncil"

    // Параметры stage-сервера:
    STAGE_HOST = "10.211.55.16"      
    STAGE_USER = "myagky"            
    STAGE_DIR  = "/home/myagky/city-council-stage"

    // Тег по номеру билда
    BUILD_TAG = "${env.BUILD_NUMBER}"
  }

  options { timestamps() }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Static: Ruff (code quality)') {
      steps {
        sh '''
          set -euo pipefail
          docker run --rm -v ${WORKSPACE}:/src ghcr.io/astral-sh/ruff:latest check /src || true
        '''
      }
    }

    stage('Static: Bandit (security)') {
      steps {
        sh '''
          set -euo pipefail
          docker run --rm -v ${WORKSPACE}:/repo -w /repo python:3.11-slim bash -lc '
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

            exec bandit -r . -ll -iii
          '
        '''
      }
    }

    stage('Static: Gitleaks (secrets)') {
      steps {
        sh '''
          set -euo pipefail
          docker run --rm --entrypoint /bin/sh -v ${WORKSPACE}:/repo -w /repo zricethezav/gitleaks:latest -lc '
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

    stage('Tests: Pytest') {
      steps {
        sh '''
          set -euo pipefail

          # 1) Виртуалка для тестов
          docker run --rm -e GIT_BRANCH=${GIT_BRANCH:-} -e GIT_COMMIT=${GIT_COMMIT:-} \
            -v ${WORKSPACE}:/repo -w /repo python:3.11-slim bash -lc "
              set -euo pipefail

              python -m venv /tmp/venv
              . /tmp/venv/bin/activate

              # 2) Зависимости
              if [ -f requirements.txt ]; then
                pip install --no-cache-dir -r requirements.txt
              else
                pip install --no-cache-dir pytest pytest-flask pytest-cov coverage
              fi

              # 3) Динамически формируем покрытие
              COVARGS=()
              for d in app blueprints models src flask_city_council; do
                if [ -d \\"$d\\" ]; then COVARGS+=(--cov=\\"$d\\"); fi
              done

              # 4) PYTHONPATH
              export PYTHONPATH=\\"${PYTHONPATH:-}:/repo:/repo/src:/repo/flask_city_council\\"

              # 5) Цель для pytest
              TARGET=\\"tests\\"
              [ -d tests ] || TARGET=\\".\\"

              # 6) Запуск pytest с обработкой кода возврата
              set +e
              pytest --maxfail=1 --disable-warnings \\"${COVARGS[@]}\\" --cov-report=term-missing \\"$TARGET\\"
              RC=$?
              set -e

              case \\"$RC\\" in
                0) echo \\"Pytests passed.\\" ;;
                5) echo \\"No tests collected — treating as success.\\" ;;
                *) exit \\"$RC\\" ;;
              esac
            "
        '''
      }
    }

    stage('Build Docker image') {
      steps {
        sh '''
          set -euo pipefail
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
            set -euo pipefail
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker push ${IMAGE_NAME}:${BUILD_TAG}
            docker push ${IMAGE_NAME}:latest
            docker logout
          '''
        }
      }
    }

    stage('Deploy to STAGE') {
      when { branch 'dev' } // деплоим на stage только из ветки dev
      steps {
        sshagent (credentials: ['stage-server-ssh']) {
          sh """
            set -euo pipefail
            ssh -o StrictHostKeyChecking=no ${STAGE_USER}@${STAGE_HOST} bash -s <<EOF
set -euo pipefail

# папка проекта на stage
mkdir -p ${STAGE_DIR}
cd ${STAGE_DIR}

# если docker-compose.yaml отсутствует — создаём один раз
if [ ! -f docker-compose.yaml ]; then
  cat > docker-compose.yaml <<'YAML'
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
YAML
fi

# .env должен быть заранее, но на первый раз можем сгенерировать шаблон
if [ ! -f .env ]; then
  cat > .env <<'ENV'
SECRET_KEY=change-me
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://cityuser:citypass@db:5432/citycouncil
FLASK_ENV=production
ENV
fi

mkdir -p uploads

# тянем новый образ и поднимаем
docker compose pull web || true
docker compose up -d

# при самом первом запуске можно разово наполнить БД демо-данными:
# docker compose exec -T web python seeds.py || true

docker compose ps
EOF
          """
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
