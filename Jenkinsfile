pipeline {
    agent any

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
	    stage ('Git Checkout') {
	            steps {
	                git branch: 'main',
	                credentialsId: '568e784d-7498-4ded-993b-0b7655931b88',
	                url: 'https://github.com/jatinkumar0/Project-1.git'
	                }
	            }
	    
	    	stage ('Creat War File') {
		steps {
		sh 'jar -cf target/dependency/webapp-runner.jar target/*.war'
		}
		}
	    
	            stage ('Deploy War File') {
	            steps {
	                sh "cp target/*.war /etc/apache-tomcat-8.5.64/webapps/"
	                }
	            }
         }
    }
