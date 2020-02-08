import boto3
import datetime
import json
import time


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

    def get_instance_by_name(self, instance_name):
        for instance in self.get_instances():
            i = instance['Instances'][0]
            tags = i['Tags']
            name = self.get_instance_name(tags)
            if name == instance_name:
                return instance

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

    def _poll_instance_state(self, instance_name, state):
        timeout = 0
        while timeout <= 10:
            instance = self.get_instance_by_name(instance_name)
            _state = instance['Instances'][0]['State']['Name']
            if timeout == 5:
                _state = 'running'
            if _state == state:
                return True
            else:
                print(f'Instance State: {_state}')
                time.sleep(2)
                timeout += 1


class SlackAWS:
    """Interact with AWS resources"""

    def __init__(self, action, instance, dry_run=True):
        self.action = action
        self.instance = instance
        self.dry_run = dry_run
        self.aws = AWSClient()

    def __repr__(self):
        return f'AWS {self.option}\nARGS:\n{self.args}'

    def run_command(self):
        commands = {
            'start': self.start_instance,
            'stop': self.stop_instance,
            'restart': self.restart_instance
        }
        command = commands.get(self.action)
        command()

    def start_instance(self):
        pass

    def stop_instance(self):
        pass

    def restart_instance(self):
        pass


def main():
    aws = AWSClient()
    i = aws._poll_instance_state('jke-control01', 'running')
    print(i)


if __name__ == '__main__':
    main()
