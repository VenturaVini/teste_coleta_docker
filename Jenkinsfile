pipeline {
    agent any
    
    environment {
        IMAGE_NAME = "minha-automacao-python"
        IMAGE_TAG = "${BUILD_NUMBER}"
        OUTPUT_DIR = "output"
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
                echo '📄 Criando Dockerfile para automação (se necessário)...'
                script {
                    if (!fileExists('Dockerfile')) {
                        writeFile file: 'Dockerfile', text: '''FROM python:3.11-slim

RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt* ./

RUN pip install --no-cache-dir -r requirements.txt || echo "Sem requirements.txt"

COPY . .

CMD ["python", "main.py"]
'''
                        echo '✅ Dockerfile criado'
                    } else {
                        echo '✅ Usando Dockerfile existente'
                    }
                }
            }
        }
        
        stage('🏗️ Build da Imagem') {
            steps {
                echo '🔨 Construindo imagem Docker...'
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                    echo "✅ Imagem construída: ${IMAGE_NAME}:${IMAGE_TAG}"
                """
            }
        }
        
        stage('🧪 Teste da Automação') {
            steps {
                echo '🧪 Testando imagem Docker...'
                sh """
                    docker run --rm ${IMAGE_NAME}:latest python --version
                    echo "✅ Python OK no container"
                """
            }
        }
        
        stage('🚀 Executar Automação') {
            steps {
                script {
                    sh "mkdir -p ${OUTPUT_DIR}"
                }
                script {
                    def envExists = fileExists('.env')
                    if (envExists) {
                        echo "🟢 .env encontrado no repositório. Usando variáveis do arquivo."
                        sh '''
                            set -a
                            source .env
                            set +a

                            docker run --rm \\
                                --name ${IMAGE_NAME}-executando \\
                                -v $(pwd)/${OUTPUT_DIR}:/app/${OUTPUT_DIR} \\
                                ${IMAGE_NAME}:latest
                        '''
                    } else {
                        try {
                            withCredentials([file(credentialsId: 'myproject-env-file', variable: 'ENV_FILE')]) {
                                echo "🟡 .env não encontrado no repo. Usando Secret File do Jenkins."
                                sh '''
                                    set -a
                                    source $ENV_FILE
                                    set +a

                                    docker run --rm \\
                                        --name ${IMAGE_NAME}-executando \\
                                        -v $(pwd)/${OUTPUT_DIR}:/app/${OUTPUT_DIR} \\
                                        ${IMAGE_NAME}:latest
                                '''
                            }
                        } catch (err) {
                            echo "⚠️ Nenhum .env encontrado e Secret File não configurado. Rodando sem variáveis extras."
                            sh """
                                docker run --rm \\
                                    --name ${IMAGE_NAME}-executando \\
                                    -v \$(pwd)/${OUTPUT_DIR}:/app/${OUTPUT_DIR} \\
                                    ${IMAGE_NAME}:latest
                            """
                        }
                    }
                }
            }
        }
        
        stage('📄 Verificar Resultados') {
            steps {
                echo '📋 Resultados da automação:'
                sh """
                    echo "=== Arquivos gerados ==="
                    ls -la ${OUTPUT_DIR} || echo "Pasta ${OUTPUT_DIR} não existe"
                """
            }
        }
    }
    
    post {
        always {
            echo '🧹 Limpando imagens antigas...'
            sh """
                docker images ${IMAGE_NAME} --format "{{.Tag}}" | grep -v latest | tail -n +3 | xargs -r -I {} docker rmi ${IMAGE_NAME}:{} || true
            """
        }
        
        success {
            echo '🎉 Pipeline finalizado com sucesso!'
        }
        
        failure {
            echo '❌ Pipeline falhou. Veja os logs para detalhes.'
        }
    }
}
