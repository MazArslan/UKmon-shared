# Copyright (C) 2018-2023 Mark McIntyre

#
# Security Groups
#

resource "aws_security_group" "default" {
  name                   = "default"
  description            = "default VPC security group"
  vpc_id                 = aws_vpc.main_vpc.id
  revoke_rules_on_delete = false
  ingress = [
    {
      description      = "http in"
      from_port        = 80
      to_port          = 80
      protocol         = "tcp"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = false
    },
    {
      cidr_blocks      = ["86.0.0.0/8"]
      description      = "SSH for Admin"
      from_port        = 22
      protocol         = "tcp"
      to_port          = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = false
    },
    {
      cidr_blocks      = []
      description      = "traffic from sg20192"
      from_port        = 0
      protocol         = "-1"
      self             = true
      to_port          = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
    },
    {
      cidr_blocks      = []
      description      = "echo from sg8115c"
      from_port        = 8
      protocol         = "icmp"
      security_groups  = [aws_security_group.launch-wizard-4.id]
      to_port          = -1
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      self             = false
    }
  ]
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    billingtag = "Management"
  }
}

resource "aws_security_group" "launch-wizard-4" {
  name        = "launch-wizard-4"
  description = "launch-wizard-4 created 2020-02-10T21:59:13.598+00:00"
  vpc_id      = aws_vpc.main_vpc.id
  ingress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = "SSH for Admin"
      from_port        = 22
      protocol         = "tcp"
      to_port          = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = false
    },
    {
      cidr_blocks      = []
      description      = "NFS"
      from_port        = 2049
      protocol         = "tcp"
      to_port          = 2049
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = true
    },
    {
      cidr_blocks      = ["86.144.129.18/32"]
      description      = "MariaDB"
      from_port        = 3306
      protocol         = "tcp"
      to_port          = 3306
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = false
    },
  ]
  egress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = ""
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "-1"
      security_groups  = []
      self             = false
      to_port          = 0
    },
  ]
  tags = {
    billingtag = "ukmon"
  }
}

resource "aws_security_group" "ec2publicsg" {
  name        = "ec2PublicSG"
  description = "Public SG used by EC2"
  vpc_id      = aws_vpc.main_vpc.id
  ingress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = "SSH for Admin"
      from_port        = 22
      protocol         = "tcp"
      to_port          = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = false
    },
    {
      cidr_blocks      = []
      description      = "NFS"
      from_port        = 2049
      protocol         = "tcp"
      to_port          = 2049
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = true
    },
  ]
  egress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = ""
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "-1"
      security_groups  = []
      self             = false
      to_port          = 0
    },
  ]
  tags = {
    billingtag = "Management"
  }
}
