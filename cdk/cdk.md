### AWS CDK

You will need to install the AWS CDK tool or use an environment like AWS Cloud9

Then from the aurora-mysql folder:

* make sure you review and are happy with the configuration selected
* this is currently setup for eu-central-1
* it will deploy a VPC, Bastion Host and Amazon Aurora Cluster with Write/Reader and an auto scale policy set
* if you want to ssh into the bastion hosts (vs use Session Manager) you will need to update the configuration file. I have commented out the configuration items, you just need to add your own

To deploy:

```
cdk deploy VPC
cdk deploy Bastion
cdk deploy AuroraMySQL
```

You can respond Y when prompted during the Bastion/Aurora stacks.