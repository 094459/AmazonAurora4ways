### Amazon Aurora - aws cli examples
**Setup VPC and networking**

In this example we are using eu-central-1 and two AZs, eu-central-1a and eu-central-1b. You can change as per your needs.

aws ec2 create-vpc --cidr-block 10.44.0.0/16 --region=eu-central-1

> this create and outputs the VPC id

aws ec2 create-subnet --vpc-id {vpcid} --availability-zone="eu-central-1a" --cidr-block 10.44.1.0/24 --region=eu-central-1 
aws ec2 create-subnet --vpc-id {vpcid} --availability-zone="eu-central-1b" --cidr-block 10.44.2.0/24 --region=eu-central-1 
 
aws ec2 create-internet-gateway --region=eu-central-1

> this creates and outputs the internet gateway id

aws ec2 attach-internet-gateway --vpc-id {vpcid} --internet-gateway-id {igwid} --region=eu-central-1 
aws ec2 create-route-table --vpc-id {vpcid} --region=eu-central-1 

> this creates and outputs the routetableid

aws ec2 create-route --route-table-id {routetableid} --destination-cidr-block 0.0.0.0/0 --gateway-id {igwid} --region=eu-central-1 
aws ec2 describe-route-tables --route-table-id {routetableid} --region=eu-central-1 
aws ec2 describe-subnets --filters "Name=vpc-id,Values={vpcid}" --query 'Subnets[*].{ID:SubnetId,CIDR:CidrBlock}' --region=eu-central-1 

> this outputs the id's of the two subnets. The first will be the Internet Gateway enabled subnet which is used for the BastionHost. The second is the Aurora subnet ID.

aws ec2 associate-route-table  --subnet-id {bastionhostsubnetid} --route-table-id {routetableid} --region=eu-central-1 
aws ec2 modify-subnet-attribute --subnet-id {bastionhostsubnetid} --map-public-ip-on-launch --region=eu-central-1

**Setup Security Group**

aws ec2 create-security-group --group-name AuroraAccess --description "Security group for Aurora access" --vpc-id {vpcid} --region=eu-central-1 

> this creates and ouputs the security group for Aurora Access

aws ec2 create-security-group --group-name Bastion --description "Security group for Bastion Host" --vpc-id {vpcid} --region=eu-central-1

> this creates and ouputs the security group for Bastion Host Access

aws ec2 authorize-security-group-ingress --group-id {bastionsgid} --protocol tcp --port 22 --cidr 0.0.0.0/0 --region=eu-central-1 
aws ec2 authorize-security-group-ingress --group-id {aurorasgid} --protocol tcp --port 3306 --cidr 0.0.0.0/0 --region=eu-central-1

**Setup Bastion Host**

> you will need to change the image-id based on the version of linux you want to deploy. choose any linux that has the AWS SSM agent pre-installed otherwise you will not be able to connect to it via Session Manager without doing the installation/configuration of that first.

aws ec2 run-instances --image-id ami-0604621e15639f0b7 --count 1 --instance-type t2.micro --security-group-ids {bastionsgid} --subnet-id {bastionhostsubnetid} --iam-instance-profile Name="gen-ec2-ssm-bastion" --region=eu-central-1 

**Setup Amazon Aurora cluster**

> Here you will need to define the names you want to use when creating the Amazon Aurora resources.

aws rds create-db-subnet-group --db-subnet-group-name {subnetgroupid} --db-subnet-group-description "Demo DB subnet group" --subnet-ids '["{bastionhostsubnetid}","{aurorasubnetid}"]' --region=eu-central-1 

> do not store the password in a file or script.

aws rds create-db-cluster --db-cluster-identifier {aurora-clusterid} --engine aurora-mysql --engine-version 5.7.12 \
 --master-username masteruser --master-user-password $PASS --db-subnet-group-name {subnetgroupid} --vpc-security-group-ids {aurorasgid} --region=eu-central-1 

aws rds create-db-instance --db-instance-identifier {db-instance-1} --availability-zone=eu-central-1a --db-cluster-identifier {aurora-clusterid} --engine aurora-mysql --db-instance-class db.r4.large --region=eu-central-1

aws rds create-db-instance --db-instance-identifier {db-instance-2} --availability-zone=eu-central-1b --db-cluster-identifier {aurora-clusterid} --engine aurora-mysql --db-instance-class db.r4.large --region=eu-central-1

aws application-autoscaling register-scalable-target --service-namespace rds \
--resource-id cluster:{aurora-clusterid} --scalable-dimension rds:cluster:ReadReplicaCount \
    --min-capacity 1 --max-capacity 3 --region=eu-central-1

aws application-autoscaling put-scaling-policy --policy-name demoauroraautoscalecli --service-namespace rds --resource-id cluster:{aurora-clusterid} --scalable-dimension rds:cluster:ReadReplicaCount --policy-type TargetTrackingScaling --target-tracking-scaling-policy-configuration file://config.json --region=eu-central-1

**Create Secret and then update password**
**Pass $secret via code, do not store in file**

aws secretsmanager create-secret --name MasterUserSecret --description "Master User password" --secret-string file://creds.json --region=eu-central-1

aws rds modify-db-cluster --db-cluster-identifier {aurora-clusterid} --apply-immediately --master-user-password $secret --region=eu-central-1

