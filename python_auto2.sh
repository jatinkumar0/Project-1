#!/bin/bash/
sudo rm -rf auto_cert.* /etc/pki/tls/certs/
sudo openssl genrsa -des3 -out auto_cert.key 1024 
sudo openssl req -new -key auto_cert.key -out auto_cert.csr
#ssh -i $keyname ec2-user@$ip sudo cp au.key auto_cert.key
sudo openssl rsa -in auto_cert.key -out auto_cert.key
openssl x509 -req -days 365 -in auto_cert.csr -signkey auto_cert.key -out auto_cert.crt
sudo mv auto_cert.* /etc/pki/tls/certs/
