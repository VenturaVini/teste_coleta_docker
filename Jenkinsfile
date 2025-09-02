pipeline {
    // Define que pode rodar em qualquer agente/máquina disponível
    agent any
    
    // Variáveis de ambiente globais - disponíveis em todos os stages
    environment {
        IMAGE_NAME = "minha-automacao-python"  // Nome da imagem Docker que será criada
        IMAGE_TAG = "${BUILD_NUMBER}"          // Tag usando número do build (1, 2, 3...)
    }
    
    // Sequência de etapas que serão executadas
    stages {
        
        // STAGE 1: Baixar código do GitHub
        stage('🔄 Checkout') {
            steps {
                echo '📥 Puxando código do GitHub...'
                // Comando que baixa o código do repositório configurado no job
                checkout scm  // SCM = Source Control Management (Git)
            }
        }
        
        // STAGE 2: Analisar o projeto baixado
        stage('🔍 Verificar Projeto') {
            steps {
                echo '📋 Verificando arquivos da automação...'
                // Lista todos os arquivos baixados do GitHub
                sh 'ls -la'
                
                // Bloco de código Groovy para lógica mais complexa
                script {
                    // Verifica se existe arquivo de dependências Python
                    if (fileExists('requirements.txt')) {
                        echo '✅ requirements.txt encontrado'
                        sh 'cat requirements.txt'  // Mostra conteúdo do arquivo
                    } else {
                        echo '⚠️ requirements.txt não encontrado'
                    }
                    
                    // Procura pelo arquivo principal Python
                    if (fileExists('main.py')) {
                        echo '✅ main.py encontrado'
                    } else if (fileExists('app.py')) {
                        echo '✅ app.py encontrado'
                    } else {
                        echo '📋 Arquivos Python encontrados:'
                        // Busca todos arquivos .py na pasta
                        sh 'find . -name "*.py" | head -5'
                    }
                }
            }
        }
        
        // STAGE 3: Criar arquivo para containerizar a aplicação
        stage('🐳 Criar Dockerfile para Automação') {
            steps {
                echo '📄 Criando Dockerfile para automação...'
                script {
                    // Só cria Dockerfile se não existir um
                    if (!fileExists('Dockerfile')) {
                        echo '🏗️ Criando Dockerfile para automação Python...'
                        
                        // Cria arquivo Dockerfile com conteúdo específico para Python
                        writeFile file: 'Dockerfile', text: '''FROM python:3.11-slim

# Instalar dependências do sistema se necessário (curl, wget, etc)
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho dentro do container
WORKDIR /app

# Copiar requirements primeiro (aproveitamento de cache do Docker)
COPY requirements.txt* ./

# Instalar dependências Python ou ignora se não tiver requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || echo "Sem requirements.txt"

# Copiar todo o código do projeto
COPY . .

# Comando que será executado quando container iniciar
CMD ["python", "main.py"]'''
                        
                        echo '✅ Dockerfile criado para automação'
                    } else {
                        echo '✅ Usando Dockerfile existente'
                    }
                }
            }
        }
        
        // STAGE 4: Construir a imagem Docker
        stage('🏗️ Build da Imagem') {
            steps {
                echo '🔨 Construindo imagem da automação...'
                sh """
                    # Constrói imagem Docker usando o Dockerfile criado
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    
                    # Cria tag "latest" para sempre ter versão mais recente
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                    
                    echo "✅ Imagem construída: ${IMAGE_NAME}:${IMAGE_TAG}"
                """
            }
        }
        
        // STAGE 5: Testar se a imagem foi criada corretamente
        stage('🧪 Teste da Automação') {
            steps {
                echo '🧪 Testando se automação executa...'
                sh """
                    echo "=== Testando automação ==="
                    # Roda container temporário só para testar Python
                    docker run --rm ${IMAGE_NAME}:latest python --version
                    echo "✅ Python está funcionando no container!"
                """
            }
        }
        
        // STAGE 6: Executar a automação de verdade
        stage('🚀 Executar Automação') {
            steps {
                echo '🤖 Executando automação Python...'
                script {
                    sh """
                        echo "=== Executando automação ==="
                        
                        # Executa a automação Python
                        # --rm: remove container quando terminar
                        # --name: nome do container enquanto roda
                        # -v: compartilha pasta output (se sua automação gerar arquivos)
                        docker run --rm \\
                            --name ${IMAGE_NAME}-executando \\
                            -v \$(pwd)/output:/app/output \\
                            ${IMAGE_NAME}:latest
                        
                        echo "✅ Automação executada!"
                    """
                }
            }
        }
        
        // STAGE 7: Verificar se tudo deu certo
        stage('📄 Verificar Resultados') {
            steps {
                echo '📋 Verificando resultados da automação...'
                sh '''
                    echo "=== Arquivos gerados ==="
                    # Verifica se automação gerou arquivos na pasta output
                    ls -la output/ || echo "Pasta output não existe"
                    
                    echo "=== Logs da execução ==="
                    echo "Automação Python executada com sucesso!"
                '''
            }
        }
    }
    
    // Ações que sempre executam (sucesso ou falha)
    post {
        // SEMPRE executa (mesmo se der erro)
        always {
            echo '🧹 Limpeza...'
            sh '''
                # Remove imagens Docker antigas para não lotar espaço
                # Mantém as 2 versões mais recentes apenas
                docker images ${IMAGE_NAME} --format "{{.Tag}}" | grep -v latest | tail -n +3 | xargs -r -I {} docker rmi ${IMAGE_NAME}:{} || true
            '''
        }
        
        // Só executa se TUDO deu certo
        success {
            echo '🎉 SUCESSO! Automação executada!'
            echo '📊 A automação Python rodou dentro do container'
            echo '📁 Verifique pasta output/ para arquivos gerados'
        }
        
        // Só executa se deu ERRO
        failure {
            echo '❌ Automação falhou!'
            echo '🔍 Verifique os logs acima para debug'
        }
    }
}