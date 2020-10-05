from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as sm,
    aws_applicationautoscaling as autoscaling,
    aws_iam as iam,
    aws_kms as kms,
    core
)

class AuroraMySQLStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        # db_subngname should be lowercase

        db_master_user_name="masteruser"
        db_cluster_name="auroramysql"
        db_name="demodb"
        db_subngname="auroramysqlsubnetgroup"

        secret = rds.DatabaseSecret(
            self,
            id="MasterUserSecret",
            username=db_master_user_name
        )

        subnet_ids = []
        for subnet in vpc.isolated_subnets:
            subnet_ids.append(subnet.subnet_id)

        subnet_group = rds.CfnDBSubnetGroup(
            self,
            id="AuroraSubnetGroup",
            db_subnet_group_description='Aurora MySQL Subnet Group',
            subnet_ids=subnet_ids,
            db_subnet_group_name=f'{db_subngname}' 
        )

        security_group = ec2.SecurityGroup(
            self,
            id="SecurityGroup",
            vpc=vpc,
            description="Allow ssh access to ec2 instances",
            allow_all_outbound=True
        )
        security_group.add_ingress_rule(ec2.Peer.ipv4('10.0.0.0/16'), ec2.Port.tcp(3306), "allow mysql through")

        db = rds.CfnDBCluster(self,'Cluster',
            engine="aurora-mysql",
            engine_mode="provisioned",
            port=3306,
            db_subnet_group_name=subnet_group.db_subnet_group_name,
            vpc_security_group_ids=[security_group.security_group_id],
            availability_zones=vpc.availability_zones,
            db_cluster_identifier=db_cluster_name,
            database_name=f"{db_name}",
            deletion_protection=False,
            storage_encrypted=True,
            enable_iam_database_authentication=True,
            master_username=secret.secret_value_from_json("username").to_string(),
            master_user_password=secret.secret_value_from_json("password").to_string()
        )
              
        db1 = rds.CfnDBInstance(
            self,
            id="Instance-01",
            engine="aurora-mysql",
            db_instance_class = "db.t2.medium",
            db_cluster_identifier=db_cluster_name,
            db_subnet_group_name=subnet_group.db_subnet_group_name,
            publicly_accessible=False
        )
        db2 = rds.CfnDBInstance(
            self,
            id="Instance-02",
            engine="aurora-mysql",
            db_instance_class = "db.t2.medium",
            db_cluster_identifier=db_cluster_name,
            db_subnet_group_name=subnet_group.db_subnet_group_name,
            publicly_accessible=False
        )

        db1.node.add_dependency(db)
        db2.node.add_dependency(db1)

        ##Role for Autoscaling Group
        role = iam.Role(self, "mysql-aas-role", assumed_by=iam.ServicePrincipal("rds.application-autoscaling.amazonaws.com"))
        role.add_to_policy(iam.PolicyStatement(resources=["*"], actions=["sts:AssumeRole"]))

        target = autoscaling.CfnScalableTarget(
            self,
            "ScalableTarget",
            service_namespace="rds",
            max_capacity=2,
            min_capacity=1,
            resource_id=f"cluster:{db_cluster_name}",
            scalable_dimension="rds:cluster:ReadReplicaCount",
            role_arn=f"{role.role_arn}"
        )

        scalepol = autoscaling.CfnScalingPolicy(
            self,
            "ScalableTargetPolicy",
            policy_name="aurora-autoscale-readers",
            policy_type="TargetTrackingScaling",
            scaling_target_id=f"cluster:{db_cluster_name}|rds:cluster:ReadReplicaCount|rds",
            target_tracking_scaling_policy_configuration=autoscaling.CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty(
                target_value=40,
                scale_in_cooldown=123,
                scale_out_cooldown=123,
                predefined_metric_specification=autoscaling.CfnScalingPolicy.PredefinedMetricSpecificationProperty(
                    predefined_metric_type="RDSReaderAverageCPUUtilization")
            )  
        )

        scalepol.node.add_dependency(target)
        target.node.add_dependency(db)


        secret_attached = sm.CfnSecretTargetAttachment(
            self,
            id="secret_attachment",
            secret_id=secret.secret_arn,
            target_id=db.ref,
            target_type="AWS::RDS::DBCluster",
        )

        core.CfnOutput(
            self,
            id="StackName",
            value=self.stack_name,
            description="Stack Name",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:stack-name"
        )

        core.CfnOutput(
            self,
            id="DatabaseName",
            value=db.database_name,
            description="Database Name",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:database-name"
        )

        core.CfnOutput(
            self,
            id="DatabaseClusterArn",
            value=f"arn:aws:rds:{self.region}:{self.account}:cluster:{db.ref}",
            description="Database Cluster Arn",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:database-cluster-arn"
        )

        core.CfnOutput(
            self,
            id="DatabaseSecretArn",
            value=secret.secret_arn,
            description="Database Secret Arn",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:database-secret-arn"
        )

        core.CfnOutput(
            self,
            id="DatabaseClusterID",
            value=db.db_cluster_identifier,
            description="Database Cluster Id",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:database-cluster-id"
        )

        core.CfnOutput(
            self,
            id="AuroraEndpointAddress",
            value=db.attr_endpoint_address,
            description="Aurora Endpoint Address",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:aurora-endpoint-address"
        )

        core.CfnOutput(
            self,
            id="DatabaseMasterUserName",
            value=db_master_user_name,
            description="Database Master User Name",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:database-master-username"
        )
