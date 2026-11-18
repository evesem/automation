// Повторение IW04: сборка и модульные тесты PHP-проекта на SSH-агенте.
pipeline {
    agent { label 'php-agent' }

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

        stage('2. Install Composer dependencies') {
            steps {
                dir('lab05') {
                    sh 'composer install --no-interaction --prefer-dist --no-progress'
                }
            }
        }

        stage('3. Run PHPUnit tests') {
            steps {
                dir('lab05') {
                    sh 'vendor/bin/phpunit --configuration phpunit.xml --log-junit phpunit-report.xml'
                }
            }
        }

        stage('4. Test report') {
            steps {
                dir('lab05') {
                    archiveArtifacts artifacts: 'phpunit-report.xml', allowEmptyArchive: true
                    echo 'PHPUnit report saved as phpunit-report.xml (JUnit XML).'
                }
            }
        }
    }

    post {
        success { echo 'Pipeline PHP build and test: SUCCESS' }
        failure { echo 'Pipeline PHP build and test: FAILURE' }
    }
}
