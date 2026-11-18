// Настройка тестового сервера с помощью Ansible на отдельном агенте.
pipeline {
    agent { label 'ansible-agent' }

    environment {
        REPO_URL = 'https://github.com/evesem/automation.git'
    }

    stages {
        stage('1. Clone Ansible playbook repository') {
            steps {
                deleteDir()
                git url: "${REPO_URL}", branch: 'main'
            }
        }

        stage('2. Run Ansible playbook') {
            steps {
                dir('lab05') {
                    sh 'ansible-playbook -i ansible/hosts.ini ansible/setup_test_server.yml'
                }
            }
        }
    }

    post {
        success { echo 'Pipeline Ansible setup: SUCCESS' }
        failure { echo 'Pipeline Ansible setup: FAILURE' }
    }
}
