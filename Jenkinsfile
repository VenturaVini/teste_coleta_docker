pipeline {
  agent any

  environment {
    IMAGE_NAME = "minha-automacao-python"
    IMAGE_TAG  = "${BUILD_NUMBER}"
    OUTPUT_DIR = "output"
  }

  stages {
    stage('🔄 Checkout') {
      steps {
        echo '📥 Clonando o repositório...'
        checkout scm
      }
    }

    stage('🐳 Build da Imagem Docker') {
      steps {
        echo '🔨 Construindo a imagem Docker...'
        sh """
          docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
          docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
          echo "✅ Imagem pronta: ${IMAGE_NAME}:${IMAGE_TAG}"
        """
      }
    }

    stage('🧪 Teste da Imagem') {
      steps {
        echo '🧪 Testando se Python roda dentro do container...'
        sh """
          docker run --rm ${IMAGE_NAME}:latest python --version
          echo "✅ Python está funcionando!"
        """
      }
    }

    stage('🚀 Executar com Docker Compose') {
      steps {
        echo '🚀 Iniciando container com Docker Compose...'
        script {
          sh """
            mkdir -p ${OUTPUT_DIR}
            docker-compose up --build -d
          """
        }
      }
    }

    stage('📄 Verificar Resultados') {
      steps {
        echo '📋 Arquivos gerados pela automação:'
        sh """
          echo "=== Conteúdo de ${OUTPUT_DIR} ==="
          ls -la ${OUTPUT_DIR} || echo "Nenhum arquivo encontrado."
        """
      }
    }
  }

  post {
    always {
      echo '🧹 Limpando containers e imagens...'
      sh """
        docker-compose down
        docker images ${IMAGE_NAME} --format "{{.Tag}}" | grep -v latest | tail -n +3 | xargs -r -I {} docker rmi ${IMAGE_NAME}:{} || true
      """
    }

    success {
      echo '🎉 Pipeline concluído com sucesso!'
    }

    failure {
      echo '❌ Falha no pipeline. Veja os logs acima para diagnosticar.'
    }
  }
}
