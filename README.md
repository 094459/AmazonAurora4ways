# Installation and configuration of Amazon Aurora

These resources are to support the Cloud Builders video on different approachs to installing and configuring Amazon Aurora. There are three different sets of resources: AWS CLI, AWS CloudFormation and AWS CDK. These are templates that provide a starting point for your own exploration of how you can automate the installation and configuration.

This will attempt to build the following:

* a VPC with two subnets in two different AZs
* security groups that control ingress to the Bastion/Aurora endpoints
* a Bastion host which you manage/connect with Session Manager
* an Amazon Aurora MySQL cluster with two instances across different AZs and an Auto Scaling policy set, installed using Amazon Aurora defaults
* Masteruser password managed by Secret Manager

You will need to tweak/adjust these for your own needs, but they should provide a good starting point.

## Choose your path

* [cli](cli/cli.md)
* [cloudformation](cloudformation/cf.md)
* [cdk](ckd/cdk.md)

Click on those to find out more. Here is the video walkthrough of me using these different approaches.

### What next

Here are some ideas of what you should explore next.

* Look at some of the debugging and testing tools that allow you to create/run tests against your automation
* Apply and automate more of the configuration steps that you might manually do
* Integrate these templates/scripts into a CI/CD pipeline to automate the process from making changes to deployment

### Additional Resources

#### Documentation and workshops

AWS CloudFormation [documentation homepage](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html)
AWS CDK [documentation homepage](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
[AWS CDK Workshop](https://cdkworkshop.com/)

#### Blog Posts

These blog posts contain more detail about configuration best practices for Amazon Aurora as well as CloudFormation.

[Deploy an Amazon Aurora PostgreSQL DB cluster with recommended best practices using AWS CloudFormation](https://aws.amazon.com/blogs/database/deploy-an-amazon-aurora-postgresql-db-cluster-with-recommended-best-practices-using-aws-cloudformation/)

---

#### Notice

I have provided these templates as a starting point. You will need to adjust and change these for your own environments and need to add additional configuration steps to make sure you follow best practices. Refer to the blog post above which provides guidance as well as links to finished templates (which I have included in this repository) to help you learn how to apply this.
