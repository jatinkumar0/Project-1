#!/bin/bash
aws configure
#CREATING VPC
read -p "Enter name for your VPC" name
read -p "Enter CIDR block for your VPC" cidr
aws ec2 create-vpc --cidr-block $cidr --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value='$name'}]'
#CREATING PUBLIC SUBNET
read -p "enter vpc ID " vpcid
read -p "Enter name for your public subnet" pub_sub
read -p "Enter CIDR block for your public subnet" cidr_pub_sub
aws ec2 create-subnet --vpc-id $vpcid  --cidr-block $cidr_pub_sub --availability-zone ap-south-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value='$pub_sub'}]'
#CREATING PRIVATE SUBNET
read -p "Enter the name of your Private Subnet" priv_sub
read -p "Enter CIDR block for your private subnet" cidr_priv_sub
aws ec2 create-subnet --vpc-id $vpcid --cidr-block $cidr_priv_sub --availability-zone ap-south-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value='$priv_sub'}]'
#CREATING A NEW ROUTE TABLE FOR PRIVATE SUBNET
aws ec2 create-route-table --vpc-id $vpcid --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Priv_route_demo}]'
#CREATING INTERNET GATEWAY
aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=igw_pub_demo}]'
#ATTACHING IGW TO VPC
read -p "Enter igw ID" igw_id
aws ec2 attach-internet-gateway --internet-gateway-id $igw_id --vpc-id $vpcid
#CREATING PEM FILE FOR LATER USE
read -p "Enter a name for your .pem file (key file)" keyname
aws ec2 create-key-pair --key-name $keyname --query 'KeyMaterial' --output text 
#sudo chmod 600 $keyname
#CREATING PUBLIC EC2 INSTANCE
#creating security group for the instance
aws ec2 create-security-group --group-name sg_pub_demo --description "security group of public instance" --vpc-id $vpcid
read -p "Enter Security group's ID" sg_pubid
read -p "Enter the public subnet ID" pub_sub_id
aws ec2 run-instances --image-id ami-04b1ddd35fd71475a --count 1 --instance-type t2.micro --key-name $keyname --subnet-id $pub_sub_id --security-group-ids $sg_pubid --associate-public-ip-address --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=JT_PUB}]'
#CREATING PRIVATE INSTANCE 
aws ec2 create-security-group --group-name sg_priv_demo --description "private instance security group of cli" --vpc-id $vpcid
read -p "Enter the sg_priv's ID" sg_privid
read -p "Enter Private subnet's ID" priv_sub_id
#CREATING NAT INSTANCE
aws ec2 run-instances --image-id ami-04b1ddd35fd71475a --count 1 --instance-type t2.micro --key-name $keyname --security-group-ids $sg_privid --subnet-id $priv_sub_id --no-associate-public-ip-address --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=JT_PRIV}]'
aws ec2 create-security-group --group-name sg_nat_demo --description "NAT instance sg" --vpc-id $vpcid
read -p "Enter nat instance's security group ID" sg_nat_id
aws ec2 run-instances --image-id ami-00999044593c895de --count 1 --instance-type t2.micro --key-name $keyname --subnet-id $pub_sub_id --security-group-ids $sg_nat --associate-public-ip-address --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=JT_NAT}]'
read -p "enter the instance id of nat instance " nat_id
aws ec2 modify-instance-attribute --instance-id $nat_id --no-source-dest-check
#CONFIGURING  SECURITY GROUPS AND ADDING INBOUND RULES TO SG
aws ec2 authorize-security-group-ingress --group-id $sg_nat_id --protocol tcp --port 80 --cidr $cidr_priv_sub
aws ec2 authorize-security-group-ingress --group-id $sg_nat_id --protocol tcp --port 80 --cidr $cidr_priv_sub
aws ec2 authorize-security-group-ingress --group-id $sg_nat_id --protocol tcp --port 443 --cidr $cidr_priv_sub
aws ec2 authorize-security-group-ingress --group-id $sg_nat_id --protocol icmp --port -1 --cidr $cidr_priv_sub
aws ec2 authorize-security-group-ingress --group-id $sg_nat_id --protocol icmp --port -1 --cidr $cidr_priv_sub
#read -p "Enter your public instance security group key name: " public_sg_key_name
read -p "Enter your public instance security group Name: " public_sg_key_value
aws ec2 create-security-group --group-name $public_sg_name --description "public security group" --vpc-id $vpcid --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value='$public_sg_key_value'}]' --query GroupId --output text
aws ec2 authorize-security-group-ingress --group-id $sg_pubid --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $sg_pubid --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $sg_pubid --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $sg_pubid --protocol tcp --port 22 --cidr 13.233.177.0/29
#aws ec2 authorize-security-group-ingress --group-id $public_sg_id --protocol tcp --port 22 --cidr 13.233.177.0/29
read -p "Enter your private instance security group key name: " private_sg_key_name
read -p "Enter your private instance security group key name: " private_sg_key_name
aws ec2 create-security-group --group-name $private_sg_name --description "private security group" --vpc-id $vpc_id --tag-specifications 'ResourceType=security-group,Tags=[{Key='$private_sg_key_name',Value='$private_sg_key_value'}]' --query GroupId --output text
aws ec2 authorize-security-group-ingress --group-id $sg_privid --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $sg_privid --protocol tcp --port 8080 --source-group $public_sg_id
aws ec2 authorize-security-group-ingress --group-id $sg_privid --protocol all --port all --source-group $nat_sg_id
aws ec2 authorize-security-group-ingress --group-id $sg_privid --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $sg_privid --protocol tcp --port 22 --cidr 13.233.177.0/29
aws ec2 authorize-security-group-ingress --group-id $sg_privid --protocol tcp --port 22 --cidr 13.233.177.0/29
aws ec2 authorize-security-group-ingress --group-id $sg_privid --protocol tcp --port 443 --cidr 0.0.0.0/0
#CONFIGURING PUBLIC ROUTE TABLE
read -p "enter the public route table id " publicrt
aws ec2 create-route --route-table-id $publicrt --destination-cidr-block 0.0.0.0/0 --gateway-id $igw_id
aws ec2 associate-route-table --route-table-id $publicrt --subnet-id $pub_sub_id
#CONFIGURING PRIVATE ROUTE TABLE
read -p "enter the private route table id " privatert
aws ec2 create-route --route-table-id $privatert --destination-cidr-block 0.0.0.0/0 --instance-id $nat_id
aws ec2 associate-route-table --route-table-id $privatert --subnet-id $priv_sub_id
# INSTALLING APACHE SERVER IN PUBLIC INSTANCE
read -p "ENTER YOUR PUBLIC IPv4" ipv4_pub 
read -p "ENTER YOUR PRIVATE IP" ipv4_priv 
ssh -i $keyname ec2-user@$ipv4_pub sudo yum install httpd
read -p "enter conf file name(name must be in *.conf) " filename
read -p "enter Servername " servername
read -p "enter server alias " serveralias
sudo ssh -i $keyname ec2-user@$ipv4_pub sudo touch $filename
sudo ssh -i $keyname ec2-user@$ipv4_pub sudo chmod 666 $filename
sudo ssh -i $keyname ec2-user@$ipv4_pub "echo '<VirtualHost *:443>' >>$filename"
sudo ssh -i $keyname ec2-user@$ipv4_pub "echo ' ServerAdmin webmaster@localhost'>>$filename"
sudo ssh -i $keyname ec2-user@$ipv4_pub "echo ' ServerName '$servername>>$filename"
sudo ssh -i $keyname ec2-user@$ipv4_pub "echo ' ServerAlias '$serveralias>>$filename"
sudo ssh -i $keyname ec2-user@$ipv4_pub "echo ' DocumentRoot /var/www/html/'>>$filename"
sudo ssh -i $keyname ec2-user@$ipv4_pub "echo ' '>>$filename"
sudo ssh -i $keyname ec2-user@$ipv4_pub "echo ' SSLProxyEngine on'>>$filename"
sudo ssh -i $keyname ec2-user@$ipv4_pub "echo ' ProxyPass / http://$ipv4_priv:8080/'>>$filename"
sudo ssh -i $keyname ec2-user@$ipv4_pub "echo ' ProxyPassReverse / http://$ipv4_priv:8080/'>>$filename"
sudo ssh -i $keyname ec2-user@$ipv4_pub "echo '</VirtualHost>'>>$filename"
sudo ssh -i $keyname ec2-user@$ipv4_pub sudo cp $filename /etc/httpd/conf.d/$filename.conf
sudo ssh -i $keyname ec2-user@$ipv4_pub sudo chmod 666 /etc/httpd/conf.d/$filename.conf
sudo ssh -i $keyname ec2-user@$ipv4_pub sudo chmod 666 /etc/hosts
sudo ssh -i $keyname ec2-user@$ipv4_pub "echo $ip $servername>>/etc/hosts"
sudo ssh -i $keyname ec2-user@$ipv4_pub sudo systemctl start httpd
sudo scp -i $keyname /home/ec2-user/$keyname ec2-user@$ipv4_pub:/home/ec2-user
sudo ssh -i $keyname ec2-user@$ipv4_pub sudo chmod 600 $keyname
sudo ssh -i $keyname ec2-user@$ipv4_pub ssh -o StrictHostKeyChecking=no ec2-user@$ipv4_priv
sudo ssh -i $keyname ec2-user@$ipv4_pub ssh -i $keyname ec2-user@$ipv4_priv sudo yum install java
sudo ssh -i $keyname ec2-user@$ipv4_pub ssh -i $keyname ec2-user@$ipv4_priv sudo wget https://mirrors.estointernet.in/apache/tomcat/tomcat-8/v8.5.61/bin/apache-tomcat-8.5.61.tar.gz
sudo ssh -i $keyname ec2-user@$ipv4_pub ssh -i $keyname ec2-user@$ipv4_priv sudo tar -xvf apache-tomcat-8.5.61.tar.gz
sudo ssh -i $keyname ec2-user@$ipv4_pub ssh -i $keyname ec2-user@$ipv4_priv sudo mv apache-tomcat-8.5.61 /etc/
sudo ssh -i $keyname ec2-user@$ipv4_pub ssh -i $keyname ec2-user@$ipv4_priv sudo mv apache-tomcat-8.5.61 /etc/
sudo ssh -i $keyname ec2-user@$ipv4_pub ssh -i $keyname ec2-user@$ipv4_priv sudo chmod +rx /etc/apache-tomcat-8.5.61/webapps/
sudo ssh -i $keyname ec2-user@$ipv4_pub ssh -i $keyname ec2-user@$ipv4_priv sudo mv jenkins.war /etc/apache-tomcat-8.5.61/webapps/
sudo ssh -i $keyname ec2-user@$ipv4_pub ssh -i $keyname ec2-user@$ipv4_priv sudo chmod +rx /etc/apache-tomcat-8.5.61/bin/
sudo ssh -i $keyname ec2-user@$ipv4_pub ssh -i $keyname ec2-user@$ipv4_priv sudo chmod +x /etc/apache-tomcat-8.5.61/bin/startup.sh
sudo ssh -i $keyname ec2-user@$ipv4_pub ssh -i $keyname ec2-user@$ipv4_priv sudo sh /etc/apache-tomcat-8.5.61/bin/startup.sh
sudo ssh -i $keyname ec2-user@$ipv4_pub sudo systemctl restart httpd
