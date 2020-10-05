#!/usr/bin/env python3
import io
from aws_cdk import core

from aurora_mysql.aurora_mysql_stack import AuroraMySQLStack
from aurora_mysql.bastion_stack import BastionStack
from aurora_mysql.vpc_stack import VpcStack


env_EU=core.Environment(region="eu-central-1")
app = core.App()

vpc_ec2_stack = VpcStack(
    scope=app,
    id="VPC",
    env=env_EU
)

bastion_stack = BastionStack(
    scope=app,
    id="Bastion",
    vpc=vpc_ec2_stack.vpc,
    env=env_EU
)

aurora_stack = AuroraMySQLStack(
    scope=app,
    id="AuroraMySQL",
    vpc=vpc_ec2_stack.vpc,
    env=env_EU
)

app.synth()
