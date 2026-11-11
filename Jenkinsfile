pipeline {
    agent any

    environment {
        IMAGE   = "legeni-webapp"
        VERSION = "1.0.${env.BUILD_NUMBER}"
        COMPOSE = "docker compose -f deploy/docker-compose.deploy.yml"
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('Tests unitaires') {
            steps {
                sh 'docker build --target test -t $IMAGE:test .'
            }
        }

        stage('Build image') {
            steps {
                sh 'docker build --build-arg APP_VERSION=$VERSION -t $IMAGE:$VERSION .'
            }
        }

        stage('Déploiement staging') {
            steps {
                sh """
                    IMAGE_REF=$IMAGE:$VERSION APP_ENV=staging APP_COLOR='#bf8700' PORT=8081 \
                        $COMPOSE -p legeni-staging up -d --wait
                """
                sh './deploy/smoke-test.sh legeni-staging $VERSION'
            }
        }

        stage('Validation production') {
            when { branch 'main' }
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    input message: "Déployer la version ${VERSION} en production ?", ok: 'Déployer'
                }
            }
        }

        stage('Déploiement production') {
            when { branch 'main' }
            steps {
                script {
                    env.PREVIOUS_IMAGE = sh(
                        script: "docker inspect -f '{{.Config.Image}}' legeni-prod-web-1 2>/dev/null || echo none",
                        returnStdout: true
                    ).trim()
                    echo "Version en production avant déploiement : ${env.PREVIOUS_IMAGE}"
                    try {
                        sh """
                            IMAGE_REF=$IMAGE:$VERSION APP_ENV=prod APP_COLOR='#2da44e' PORT=8082 \
                                $COMPOSE -p legeni-prod up -d --wait
                            ./deploy/smoke-test.sh legeni-prod $VERSION
                        """
                    } catch (err) {
                        if (env.PREVIOUS_IMAGE != 'none') {
                            echo "Smoke test KO : retour à ${env.PREVIOUS_IMAGE}"
                            sh """
                                IMAGE_REF=$PREVIOUS_IMAGE APP_ENV=prod APP_COLOR='#2da44e' PORT=8082 \
                                    $COMPOSE -p legeni-prod up -d --wait
                            """
                        }
                        error "Déploiement production échoué, rollback effectué"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} : version ${VERSION} déployée"
        }
        failure {
            echo "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER} en échec"
        }
    }
}
