#!/bin/bash
sudo yum install httpd 
echo "Enter your public instace's IPv4"
read  ip_pub
echo "enter your private IP:"
read ip_priv
#sudo yum install httpd
sudo yum install java
sudo yum install -y mod_ssl
openssl genrsa -des3 -out automation.key 1024
openssl rsa -in automation.key -out automation.key
openssl req -new -key automation.key -out automation.csr
openssl x509 -req -days 365 -in automation.csr -signkey automation.key -out automation.crt
sudo cp -r automation.key automation.crt automation.csr /etc/pki/tls/certs/
mkdir -p /var/www/html/automation
touch /etc/httpd/conf.d/automation.conf 
touch /var/www/html/automation/auto.html 
cat > /etc/httpd/conf.d/automation.conf << EOF 
<VirtualHost *:443>
	 ServerAdmin webmaster@localhost 
	 ServerName  jatin-jenkins.cloudtechner.com
	 DocumentRoot /var/www/html/automation	

	 SSLEngine on
	 SSLCertificateFile /etc/pki/tls/certs/automation.crt 
	 SSLCertificateKeyFile /etc/pki/tls/certs/automation.key

	 ProxyPass / http://172.31.0.97:8080/
	 ProxyPassReverse / http://172.31.0.97:8080/ 
	 
	 #LogLevel info ssl:warn ErrorLog /etc/httpd/error.log
	 #CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOF
cat > /var/www/html/automation/auto.html << EOF
<html>
<body>
<h1> automation testing works </h1>
</body>
</html>
EOF
echo "$ip_pub" >> /etc/hosts
ssh -i aws ec2-user@$ip_priv sudo wget https://mirrors.estointernet.in/apache/tomcat/tomcat-8/v8.5.61/bin/apache-tomcat-8.5.61.tar.gz
ssh -i aws ec2-user@$ip_priv sudo tar -xvf apache-tomcat-8.5.61.tar.gz
ssh -i aws ec2-user@$ip_priv sudo cp -r apache-tomcat-8.5.61 /etc
ssh -i aws ec2-user@$ip_priv sudo chmod +x /etc/apache-tomcat-8.5.61/bin
#ssh -i aws ec2-user@$ip_priv cd /etc/apache-tomcat-8.5.61/bin/
#ssh -i aws ec2-user@$ip_priv cd /etc/apache-tomcat-8.5.61/bin/
ssh -i aws ec2-user@$ip_priv sudo sh /etc/apache-tomcat-8.5.61/bin/startup.sh
ssh -i aws ec2-user@$ip_priv exit
ssh -i aws ec2-user@$ip_priv exit
sudo systemctl restart httpd.service
#sudo systemctl restart httpd.service

