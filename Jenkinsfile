pipeline {
    agent any
    
    environment {
        SERVICE = 'exchange'
        NAME = "tpenha05/${env.SERVICE}"
        REGISTRY_CREDENTIALS = 'dockerhub-credentials'
    }
    
    stages {
        stage('Install Dependencies') {
            steps {
                script {
                    sh '''
                        python3 --version || echo "Python not found"
                        pip3 --version || echo "Pip not found"
                        
                        # Se existir requirements.txt, instalar dependências
                        if [ -f "requirements.txt" ]; then
                            pip3 install -r requirements.txt || echo "Failed to install requirements"
                        fi
                    '''
                }
            }
        }        
        stage('Build & Push Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: env.REGISTRY_CREDENTIALS, 
                                                   usernameVariable: 'USERNAME', 
                                                   passwordVariable: 'TOKEN')]) {
                        sh """
                            docker login -u \$USERNAME -p \$TOKEN
                            docker build -t ${env.NAME}:latest .
                            docker build -t ${env.NAME}:${env.BUILD_NUMBER} .
                            docker push ${env.NAME}:latest
                            docker push ${env.NAME}:${env.BUILD_NUMBER}
                        """
                    }
                }
            }
        }
    }
}