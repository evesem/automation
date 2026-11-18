// Размещение PHP-проекта на тестовом сервере через Ansible.
pipeline {
    agent { label 'ansible-agent' }

    environment {
        REPO_URL = 'https://github.com/evesem/automation.git'
    }

    stages {
        stage('1. Clone PHP repository') {
            steps {
                deleteDir()
                git url: "${REPO_URL}", branch: 'main'
            }
        }

        stage('2. Copy project files to test server') {
            steps {
                dir('lab05') {
                    sh 'ansible-playbook -i ansible/hosts.ini ansible/deploy_php_project.yml'
                }
            }
        }

        stage('3. Verify deployed application') {
            steps {
                sh 'curl -fsS http://test-server/ | grep -q "Calculator"'
                echo 'PHP application is available at http://localhost:8081/'
            }
        }
    }

    post {
        success { echo 'Pipeline PHP deploy: SUCCESS' }
        failure { echo 'Pipeline PHP deploy: FAILURE' }
    }
}
