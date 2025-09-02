pipeline {
    agent any

    environment {
        IMAGE_NAME = "minha-automacao-python"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('🔄 Checkout') {
            steps {
                echo '📥 Puxando código do GitHub...'
                checkout scm
            }
        }

        stage('🔍 Verificar Projeto') {
            steps {
                echo '📋 Verificando arquivos da automação...'
                sh 'ls -la'

                script {
                    if (fileExists('requirements.txt')) {
                        echo '✅ requirements.txt encontrado'
                        sh 'cat requirements.txt'
                    } else {
                        echo '⚠️ requirements.txt não encontrado'
                    }

                    if (fileExists('main.py')) {
                        echo '✅ main.py encontrado'
                    } else if (fileExists('app.py')) {
                        echo '✅ app.py encontrado'
                    } else {
                        echo '📋 Arquivos Python encontrados:'
                        sh 'find . -name "*.py" | head -5'
                    }
                }
            }
        }

        stage('🐳 Criar Dockerfile para Automação') {
            steps {
                echo '📄 Verificando Dockerfile...'
                script {
                    if (!fileExists('Dockerfile')) {
                        echo '🏗️ Criando Dockerfile padrão para automação...'
                        writeFile file: 'Dockerfile', text: '''FROM python:3.11-slim

RUN apt-get update && apt-get install -y \\
    curl wget && \\
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt || echo "Sem requirements.txt"

COPY . .

CMD ["python", "main.py"]
'''
                    } else {
                        echo '✅ Usando Dockerfile existente'
                    }
                }
            }
        }

        stage('🏗️ Build da Imagem') {
            steps {
                echo '🔨 Construindo imagem com docker-compose...'
                sh '''
                    docker-compose build
                '''
            }
        }

        stage('🧪 Teste da Imagem') {
            steps {
                echo '🧪 Testando se Python está funcionando na imagem...'
                sh '''
                    docker run --rm ${IMAGE_NAME}_app python --version
                '''
            }
        }

        stage('🚀 Executar Automação') {
            steps {
                echo '🚀 Executando automação com Docker Compose...'
                sh '''
                    docker-compose up --abort-on-container-exit
                '''
            }
        }

        stage('📄 Verificar Resultados') {
            steps {
                echo '📋 Verificando resultados da automação...'
                sh '''
                    echo "=== Arquivos gerados ==="
                    ls -la output/ || echo "Pasta output não existe"

                    echo "=== Fim da execução ==="
                '''
            }
        }
    }

    post {
        always {
            echo '🧹 Limpeza...'
            sh '''
                docker-compose down || true

                # Remove imagens antigas (mantém as 2 mais recentes)
                docker images ${IMAGE_NAME} --format "{{.Tag}}" | grep -v latest | tail -n +3 | xargs -r -I {} docker rmi ${IMAGE_NAME}:{} || true
            '''
        }

        success {
            echo '🎉 SUCESSO! Automação executada com docker-compose!'
        }

        failure {
            echo '❌ Falha na automação!'
            echo '🔍 Veja os logs acima para identificar o problema.'
        }
    }
}
