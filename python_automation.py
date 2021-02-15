import boto3
import time
import paramiko

from mypy_boto3_ec2_instance_connect import EC2InstanceConnectClient
first_option=int(input("default VPC name is Jatin_VPC and default Cidr-Block is 10.0.0.0/16\nPress 0 if you want to continue with default"
      "\nPress 1 if you want to change \n 2.Exit \n"))
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
while(first_option!=2):
    if(first_option==2):
        print("OK")
    elif(first_option==1):
        back=input("press 0 to go back <--\n1 to continue")
        if(back==0):
            print("OK")
        if(back==1):
            vpc_name=input("Enter the name for your VPC")
            vpc_cidr=input("Enter CIDR block for your VPC")
            vpc = ec2.create_vpc(CidrBlock=vpc_cidr)
            vpc.create_tags(Tags=[{"Key": "Name", "Value": vpc_name}])
            vpc.wait_until_available()
            subnet_pub = ec2.create_subnet(CidrBlock='10.0.1.0/24', VpcId=vpc.id)
            subnet_priv = ec2.create_subnet(CidrBlock='10.0.2.0/24', VpcId=vpc.id)
            subnet_pub.create_tags(Tags=[{"Key": "Name", "Value": "Pub_sub"}])
            subnet_priv.create_tags(Tags=[{"Key": "Name", "Value": "Priv_sub"}])
            print("VPC and subnets created sucessfuly")

    else:
        print("Invalid OPtion")
    if(first_option==0):
        vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
        vpc.create_tags(Tags=[{"Key":"Name","Value":"test_sir2_VPC"}])
        vpc.wait_until_available()
        print(vpc.id)
        subnet_pub = ec2.create_subnet(CidrBlock = '10.0.1.0/24', VpcId= vpc.id , AvailabilityZone='ap-south-1b')
        subnet_priv = ec2.create_subnet(CidrBlock = '10.0.2.0/24', VpcId = vpc.id , AvailabilityZone='ap-south-1b')
        #ec2Client.modify_vpc_attribute(VpcId=vpc.id, EnableDnsSupport={'Value': True})
        subnet_pub.create_tags(Tags=[{"Key":"Name","Value":"Pub_sub"}])
        subnet_priv.create_tags(Tags=[{"Key":"Name","Value":"Priv_sub"}])
        print("VPC and subnets created sucessfuly")

        # create an internet gateway and attach it to VPC
        igw = ec2.create_internet_gateway()
        vpc.attach_internet_gateway(InternetGatewayId=igw.id)
        print("IGW attached successfully")
        #creating security groups
        sg_pub = ec2.create_security_group(GroupName='demo-sg-pub', Description='Python assignment-2', VpcId=vpc.id)
        sg_priv = ec2.create_security_group(GroupName='demo-sg-priv', Description='Python assignment-2', VpcId=vpc.id)
        sg_nat = ec2.create_security_group(GroupName='demo-sg-nat', Description='Python assignment-2', VpcId=vpc.id)
        #sg-pub
        sg_pub.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)
        sg_pub.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=80, ToPort=80)
        sg_pub.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=443, ToPort=443)
        sg_pub.authorize_ingress(CidrIp='13.233.177.0/29', IpProtocol='tcp', FromPort=22, ToPort=22)
        ###################
        sg_nat_auth = client.authorize_security_group_ingress(
                GroupId=sg_nat.id,
                IpPermissions=[
                    {'IpProtocol': 'tcp',
                     'FromPort': 80,
                     'ToPort': 80,
                     'IpRanges': [{'CidrIp':'10.0.2.0/24'}]},
                    {'IpProtocol': 'tcp',
                     'FromPort': 22,
                     'ToPort': 22,
                     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                    {'IpProtocol': 'tcp',
                     'FromPort': 443,
                     'ToPort': 443,
                     'IpRanges': [{'CidrIp':'0.0.0.0/0'}]},
                    {'IpProtocol': '-1',
                     'FromPort': -1,
                     'ToPort': -1,
                     'UserIdGroupPairs': [{
                    'GroupId': sg_priv.id }]},
                    {'IpProtocol': 'icmp',
                     'FromPort': -1,
                     'ToPort': -1,
                     'IpRanges': [{'CidrIp':'10.0.2.0/24'}]}
                ])
        #print('Ingress Successfully Set %s')
        # private security group inbound rule added
        sg_priv_auth = client.authorize_security_group_ingress(
                GroupId=sg_priv.id,
                IpPermissions=[
                    {'IpProtocol': 'tcp',
                     'FromPort': 80,
                     'ToPort': 80,
                     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                    {'IpProtocol': 'tcp',
                     'FromPort': 22,
                     'ToPort': 22,
                     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                    {'IpProtocol': 'tcp',
                     'FromPort': 443,
                     'ToPort': 443,
                     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                    {'IpProtocol': 'tcp',
                     'FromPort': 22,
                     'ToPort': 22,
                     'IpRanges': [{'CidrIp': '10.0.1.0/24' }]},
                    {'IpProtocol': '-1',
                     'FromPort': -1,
                     'ToPort': -1,
                     'UserIdGroupPairs': [{
                    'GroupId': sg_nat.id }]},
                    {'IpProtocol': 'tcp',
                     'FromPort': 8080,
                     'ToPort': 8080,
                     'UserIdGroupPairs': [{
                    'GroupId': sg_pub.id }]}
                ])
        #print('Ingress Successfully Set %s' % data3)
        #sg-nat
        # sg_nat.authorize_ingress(CidrIp='10.0.2.0/24', IpProtocol='tcp', FromPort=80, ToPort=80)
        # sg_nat.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)
        # sg_nat.authorize_ingress(CidrIp='10.0.2.0/24', IpProtocol='tcp', FromPort=443, ToPort=443)
        # sg_nat.authorize_ingress(CidrIp='10.0.2.0/24', IpProtocol='icmp', FromPort=-1, ToPort=-1)
        # sg_nat.authorize_ingress(GroupId=sg_priv.id, IpProtocol='-1', FromPort=-1, ToPort=-1)
        # #sg-priv
        # sg_priv.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=80, ToPort=80)
        # sg_priv.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=443, ToPort=443)
        # sg_priv.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)
        # sg_priv.authorize_ingress(CidrIp='10.0.2.0/24', IpProtocol='tcp', FromPort=22, ToPort=22)
        # sg_priv.authorize_ingress(GroupId=sg_pub.id, IpProtocol='tcp', FromPort=8080, ToPort=8080)
        # sg_priv.authorize_ingress(GroupId=sg_nat.id, IpProtocol='-1', FromPort=-1, ToPort=-1)
        # Create Public route table
        pub_rt = ec2.create_route_table(VpcId=vpc.id)
        print(pub_rt.id)
        ec2.create_tags(Resources=[pub_rt.id], Tags=[{'Key': 'Name', 'Value': 'demo_pub_rt' }])
        # private route table creation
        priv_rt = ec2.create_route_table(VpcId=vpc.id)
        print(priv_rt.id)
        ec2.create_tags(Resources=[priv_rt.id], Tags=[{'Key': 'Name', 'Value': 'demo_priv_rt' }])
        #list of subnet_ids
        sub_id=[subnet_pub.id,subnet_priv.id]
        #Creating public_ec2 instances

        sg_pub_id=["sg_pub.id"]
        #creating private_ec2 instance
        # priv_instance = ec2.create_instances(
        #     ImageId = 'ami-08e0ca9924195beba',
        #     MinCount = 1,
        #     MaxCount = 1,
        #     InstanceType = 't2.micro',
        #     SecurityGroupIds = sg_pub_id ,
        #     KeyName = 'final_9',
        #     SubnetId = sub_id[1] )
        priv_instance = ec2.create_instances(ImageId = 'ami-08e0ca9924195beba',MinCount = 1,MaxCount = 1,
                                              InstanceType = 't2.micro',KeyName = 'final_9',
                                             NetworkInterfaces=[{
                                                 "DeviceIndex": 0,
                                                 'SubnetId': sub_id[1],
                                                 'Groups': [sg_priv.id]
                                                 #"AssociatePublicIpAddress": False
                                             }]
                                             )
        pub_instance = ec2.create_instances(
            ImageId='ami-08e0ca9924195beba',
            MinCount=1,
            MaxCount=1,
            InstanceType = 't2.micro',
            KeyName='final_9',
            #SubnetId = sub_id[0],
            NetworkInterfaces=[{
                "DeviceIndex": 0,
                'SubnetId':sub_id[0],
                    'Groups': [sg_pub.id],
                "AssociatePublicIpAddress": True
            }]
            )
        #creating NAT instance
        nat_instance = ec2.create_instances(
            ImageId = 'ami-00999044593c895de',
            MinCount = 1,
            MaxCount = 1,
            InstanceType = 't2.micro',
            KeyName = 'final_9',
            #SubnetId = sub_id[0],
            NetworkInterfaces=[{
                "DeviceIndex": 0,
                'SubnetId':sub_id[0],
                    'Groups': [sg_nat.id],
                "AssociatePublicIpAddress": True
            }]
            )
        pub_instance.wait_until_running()
        priv_instance.wait_until_running()
        nat_instance.wait_until_running()
        result = client.modify_instance_attribute(InstanceId=nat_instance[0].id, SourceDestCheck={'Value': False})
        ec2.create_tags(Resources=[pub_instance[0].id], Tags=[{'Key': 'Name', 'Value': 'sir2_pub_instance' }])
        ec2.create_tags(Resources=[priv_instance[0].id], Tags=[{'Key': 'Name', 'Value': 'sir2_priv_instance' }])
        ec2.create_tags(Resources=[nat_instance[0].id], Tags=[{'Key': 'Name', 'Value': 'sir2_nat_instance' }])
        #time.sleep(180)
        pub_route = pub_rt.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=igw.id)
        priv_route = priv_rt.create_route(DestinationCidrBlock='0.0.0.0/0', InstanceId=nat_instance[0].id )
        pub_rt.associate_with_subnet(SubnetId=sub_id[0])
        priv_rt.associate_with_subnet(SubnetId=sub_id[1])
        def get_public_ip(instance_id):
            ec2_client = boto3.client("ec2", region_name="ap-south-1")
            reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")
            for reservation in reservations:
                for instance in reservation['Instances']:
                    return(instance.get("PublicIpAddress"))
        pub_instance_id=pub_instance[0].id
        pub_ip=get_public_ip(pub_instance_id)
        priv_ip=priv_instance[0].private_ip_address
        key="final_9.pem"
        localpath = 'final_9.pem'
        remotepath = 'final_9.pem'
        #localpath1 = 'copy.txt'
        #emotepath1 = 'copy.txt'
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=pub_ip,username="ec2-user",key_filename=key)
        sftp=ssh.open_sftp()
        sftp.put(localpath,remotepath)
        #sftp.put(localpath1,remotepath1)
        sftp.close()
        ssh.close()
        key = paramiko.RSAKey.from_private_key_file("final_9.pem")
        print(pub_ip)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(key)
        try:
            # Here 'ubuntu' is user name and 'instance_ip' is public IP of EC2
            client.connect(hostname=pub_ip, username="ec2-user", pkey=key)
            # Execute a command(cmd) after connecting/ssh to an instance
            #stdin, stdout, stderr = client.exec_command("touch abc_jatin_demo_vpc")
            stdin, stdout, stderr = client.exec_command("sudo yum install httpd -y")
            time.sleep(10)
            stdin, stdout, stderr = client.exec_command("sudo chmod 600 final_9.pem")
            stdin, stdout, stderr = client.exec_command("sudo systemctl start httpd")
            stdin, stdout, stderr = client.exec_command("sudo touch filename")
            stdin, stdout, stderr = client.exec_command("sudo chmod 666 filename")
            stdin, stdout, stderr = client.exec_command("echo '<VirtualHost *:80>' >>filename")
            stdin, stdout, stderr = client.exec_command("echo ' ServerAdmin webmaster@localhost'>>filename")
            stdin, stdout, stderr = client.exec_command("echo ' ServerName ja98.com'>>filename")
            stdin, stdout, stderr = client.exec_command("echo ' ServerAlias www.ja98.com'>>filename")
            stdin, stdout, stderr = client.exec_command("echo ' DocumentRoot /var/www/html/'>>filename")
            stdin, stdout, stderr = client.exec_command("echo ' SSLEngine on'>>filename")
            stdin, stdout, stderr = client.exec_command("echo ' SSLCertificateFile /etc/pki/tls/certs/auto_cert.crt'>>filename")
            stdin, stdout, stderr = client.exec_command("echo ' SSLCertificateKeyFile /etc/pki/tls/certs/auto_cert.key'>>filename")
            stdin, stdout, stderr = client.exec_command("echo ' '>>filename")
            stdin, stdout, stderr = client.exec_command("echo ' SSLProxyEngine on'>>filename")
            stdin, stdout, stderr = client.exec_command("echo ' ProxyPass / http://"+priv_ip+":8080/'>>filename")
            stdin, stdout, stderr = client.exec_command("echo ' ProxyPassReverse / http://"+priv_ip+":8080/'>>filename")
            stdin, stdout, stderr = client.exec_command("echo '</VirtualHost>'>>filename")
            stdin, stdout, stderr = client.exec_command("sudo yum install -y mod_ssl")
            stdin, stdout, stderr = client.exec_command("sudo cp filename /etc/httpd/conf.d/filename.conf")
            stdin, stdout, stderr = client.exec_command("sudo chmod 666 /etc/httpd/conf.d/filename.conf")
            stdin, stdout, stderr = client.exec_command("sudo chmod 666 /etc/hosts")
            stdin, stdout, stderr = client.exec_command("ssh -o StrictHostKeyChecking=no ec2-user@"+priv_ip+" uptime")
            stdin, stdout, stderr = client.exec_command("ssh -i final_9.pem ec2-user@"+priv_ip+" sudo yum install java -y")
            stdin, stdout, stderr = client.exec_command("ssh -i final_9.pem ec2-user@"+priv_ip+" sudo wget https://mirrors.estointernet.in/apache/tomcat/tomcat-8/v8.5.61/bin/apache-tomcat-8.5.61.tar.gz")
            time.sleep(10)
            stdin, stdout, stderr = client.exec_command("ssh -i final_9.pem ec2-user@"+priv_ip+" sudo tar -xvf apache-tomcat-8.5.61.tar.gz")
            time.sleep(10)
            stdin, stdout, stderr = client.exec_command("ssh -i final_9.pem ec2-user@"+priv_ip+" sudo cp -r apache-tomcat-8.5.61 /etc/")
            stdin, stdout, stderr = client.exec_command("ssh -i final_9.pem ec2-user@"+priv_ip+" sudo wget https://get.jenkins.io/war/2.272/jenkins.war")
            time.sleep(10)
            stdin, stdout, stderr = client.exec_command("ssh -i final_9.pem ec2-user@"+priv_ip+" sudo chmod +rx /etc/apache-tomcat-8.5.61/webapps/")
            stdin, stdout, stderr =client.exec_command("ssh -i final_9.pem ec2-user@"+priv_ip+" sudo mv jenkins.war /etc/apache-tomcat-8.5.61/webapps/")
            stdin, stdout, stderr =client.exec_command("ssh -i final_9.pem ec2-user@"+priv_ip+" sudo chmod +rx /etc/apache-tomcat-8.5.61/bin/startup.sh")
            stdin, stdout, stderr =client.exec_command("ssh -i final_9.pem ec2-user@"+priv_ip+" sudo sh /etc/apache-tomcat-8.5.61/bin/startup.sh")
            stdin, stdout, stderr =client.exec_command(" sudo systemctl restart httpd")
            print(stdout.read())
            # close the client connection once the job is done
            client.close()
        except Exception as e:
            print(e)
    first_option = int(input(
        "default VPC name is Jatin_VPC and default Cidr-Block is 10.0.0.0/16\nPress 0 if you want to continue with default"
            "\nPress 1 if you want to change \n 2.Exit \n"))
