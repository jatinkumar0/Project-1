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
         stage ('Creat War File') {
	            steps {
	                sh 'java -jar target/dependency/webapp-runner.jar target/jatin.war'
	                }
	            }
	            stage ('Deploy War File') {
	            steps {
	                sh "cp target/jatin.war /etc/apache-tomcat-8.5.61/webapps/"
	                }
	            }
        }
    }
