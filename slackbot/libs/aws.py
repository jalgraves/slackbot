import boto3


class AWSClient:
    """Interact with AWS resources"""

    def __init__(self, region='us-east-2'):
        self.region = region

    def __repr__(self):
        return f'AWS {self.region}'

    def get_client(self, resource):
        return boto3.client(resource, region_name=self.region)

    @property
    def ec2(self):
        return self.get_client('ec2')

    def get_instances(self) -> list:
        ec2 = self.ec2
        instances = ec2.describe_instances()
        return instances['Reservations']

    def get_instance_name(self, instance_tags: list) -> str:
        instance_name = ''
        for tag in instance_tags:
            if tag['Key'] == 'Name':
                instance_name = tag['Value']
                break
        return instance_name

    def get_instance_id(self, instance_name):
        instance_map = {}
        instances = self.get_instances()
        for instance in instances:
            inst = instance['Instances'][0]
            name = self.get_instance_name(inst['Tags'])
            if name:
                inst_id = inst['InstanceID']
                instance_map[name] = inst_id
        instance_id = instance_map.get(instance_name)
        return instance_id

    def stop_instance(self, instance_id, dry_run=True):
        instances = []
        instances.append(instance_id)
        response = self.ec2.stop_instances(InstanceIds=instances, DryRun=dry_run)
        return response

    def start_instance(self, instance_id, dry_run=True):
        instances = []
        instances.append(instance_id)
        response = self.ec2.start_instances(InstanceIds=instances, DryRun=dry_run)
        return response

    def restart_instance(self, instance_id, dry_run=True):
        instances = []
        instances.append(instance_id)
        response = self.ec2.reboot_instances(InstanceIds=instances, DryRun=dry_run)
        return response


class SlackAWS:
    """Interact with AWS resources"""

    def __init__(self, option, args):
        self.option = option
        self.args = args
        self.aws = AWSClient()

    def __repr__(self):
        return f'AWS {self.option}\nARGS:\n{self.args}'

    def run_command(self):
        commands = {
            'start': self.start_instance,
            'stop': self.stop_instance,
            'restart': self.restart_instance
        }
        command = commands.get(self.option)
        command()

    def start_instance(self):
        pass

    def stop_instance(self):
        pass

    def restart_instance(self):
        pass


def main():
    aws = SlackAWS()
    print(aws)


if __name__ == '__main__':
    main()
