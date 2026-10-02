pipeline {
    agent any

    parameters {
        booleanParam(name: 'HEADLESS', defaultValue: true, description: 'Run browser headless')
    }

    environment {
        HEADLESS = "${params.HEADLESS}"
        ALLURE_RESULTS_DIR = 'reports/allure-results'
    }

    options {
        timestamps()
        ansiColor('xterm')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                sh 'pip install uv'
                sh 'uv sync --all-extras'
            }
        }

        stage('Install Browsers') {
            steps {
                sh 'uv run playwright install --with-deps chromium'
            }
        }

        stage('Test') {
            steps {
                sh 'uv run pytest'
            }
        }

        stage('Report') {
            steps {
                sh 'uv run allure generate reports/allure-results -o reports/allure-report --clean'
            }
        }

        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'reports/**, test-results/**', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            // Re-archive in post.always so artifacts survive even if an earlier stage
            // aborts the build before the Archive stage runs.
            archiveArtifacts artifacts: 'reports/**, test-results/**', allowEmptyArchive: true
        }
        failure {
            echo 'Tests failed. See archived reports/ and test-results/ for diagnostics.'
        }
    }
}
