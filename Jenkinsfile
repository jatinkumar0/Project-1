pipeline {
agent any

stages{
 
stage('BUILD')
{
steps{
 echo "Hello everyone"
}
}

stage('Deploy'){
steps{
echo "Deploying"
}
}

 stage('MKDIR')
 {
  steps{
  sh "mkdir /ec2-user@ip-172-31-0-46/xyz.conf"  
  
  }
 }
 
 
 
 
 
}

}
