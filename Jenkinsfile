pipeline {
    agent any
    tools {
        maven 'maven'
        }
    stages {
        stage ('Compile') {
            steps {
                sh 'mvn install'
                }
            }     
        stage ('Package') {
            steps {
                sh 'mvn package'
                }
            }
        stage ('Install') {
            steps {
                sh 'mvn install'
                }
            }
        }
    }
