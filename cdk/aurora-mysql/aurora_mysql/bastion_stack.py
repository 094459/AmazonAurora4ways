from aws_cdk import (
    aws_ec2 as ec2,
    core
)

ec2_type = "t3.micro"

with open("assets/bastion.sh") as f:
    user_data = f.read()

class BastionStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bastion = ec2.BastionHostLinux(
            self,
            id="BastionHost",
            vpc=vpc,
            instance_name="BastionHost",
            instance_type=ec2.InstanceType(ec2_type),
            subnet_selection=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            )
        )
        
        

        ## Setup key_name for EC2 instance login if you don't use Session Manager
        ## Create keypair in AWS console
        ## Change .any_ipv4 to a specific IP address/range to reduce attack surface

        #key_name = "{keypair}"
        #bastion.allow_ssh_access_from(ec2.Peer.any_ipv4())
        #bastion.allow_ssh_access_from(ec2.Peer.ipv4('10.44.0.0/24'))
        #bastion.instance.instance.add_property_override("KeyName", key_name)

        ec2.CfnEIP(self, id="BastionHostEIP", domain="vpc", instance_id=bastion.instance_id)

        core.CfnOutput(
            self,
            id="BastionPrivateIP",
            value=bastion.instance_private_ip,
            description="BASTION Private IP",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:bastion-private-ip"
        )

        core.CfnOutput(
            self,
            id="BastionPublicIP",
            value=bastion.instance_public_ip,
            description="BASTION Public IP",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:bastion-public-ip"
        )
