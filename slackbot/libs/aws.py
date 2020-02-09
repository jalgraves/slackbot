import boto3
import datetime
import json
import os
import time

from typing import Any, Union


def _get_config() -> dict:
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, 'config.json')) as f:
        config = json.load(f)
    return config


def _get_client(self, resource, region) -> boto3.client:
    return boto3.client(resource, region_name=region)


def _get_instances(client) -> list:
    instances = client.describe_instances()
    return instances['Reservations']


def _instance_name_from_tags(instance_tags: list) -> str:
    instance_name = ''
    for tag in instance_tags:
        if tag['Key'] == 'Name':
            instance_name = tag['Value']
            break
    return instance_name


class AWSClient:
    """Interact with AWS resources"""

    def __init__(self, region='us-west-2'):
        self.region = region

    def __repr__(self) -> str:
        return f'AWS {self.region}'

    @property
    def ec2(self):
        return _get_client('ec2', self.region)

    @property
    def instances(self) -> list:
        return _get_instances(self.ec2)

    def get_instance_id(self, instance_name: str) -> Union[str, None]:
        instance_id = ''
        for i in self.instances:
            instance = i['Instances'][0]
            name = _instance_name_from_tags(instance['Tags'])
            if name == instance_name:
                instance_id = instance['InstanceId']
        return instance_id

    def instance_exists(self, instance_name: str) -> bool:
        exists = False
        for i in self.instances:
            instance = i['Instances'][0]
            name = _instance_name_from_tags(instance['Tags'])
            if name == instance_name:
                exists = True
        return exists

    def get_instance_by_name(self, instance_name: str) -> Union[str, None]:
        instance = None
        for i in self.instances:
            data = i['Instances'][0]
            tags = data['Tags']
            name = _instance_name_from_tags(tags)
            if name == instance_name:
                instance = i
                break
        return instance

    def stop_instance(self, instance_name: str, dry_run: bool = True) -> dict:
        instance_id = self.get_instance_id(instance_name)
        response = self.ec2.stop_instances(InstanceIds=[instance_id], DryRun=dry_run)
        self._poll_instance_state(instance_name, 'stopped')
        return response

    def start_instance(self, instance_name: str, dry_run: bool = True) -> dict:
        instance_id = self.get_instance_id(instance_name)
        response = self.ec2.start_instances(InstanceIds=[instance_id], DryRun=dry_run)
        self._poll_instance_state(instance_name, 'running')
        return response

    def reboot_instance(self, instance_name: str, dry_run: bool = True) -> dict:
        instance_id = self.get_instance_id(instance_name)
        response = self.ec2.reboot_instances(InstanceIds=[instance_id], DryRun=dry_run)
        return response

    def restart_instance(self, instance_name: str) -> list:
        """Stop then start an AWS EC2 instance"""
        stop_data = self.stop_instance(instance_name, dry_run=False)
        start_data = self.start_instance(instance_name, dry_run=False)
        return [stop_data, start_data]

    def get_instance_state(self, instance_name: str) -> Union[str, Any]:
        instance = self.get_instance_by_name(instance_name)
        return instance['Instances'][0]['State']['Name']

    def _poll_instance_state(self, instance_name: str, state: str) -> Union[bool, None]:
        instance_state = ''
        timeout = 0
        while timeout <= 50:
            instance = self.get_instance_by_name(instance_name)
            _state = instance['Instances'][0]['State']['Name']
            if _state == state:
                print(f'Instance {_state}')
                instance_state = _state
                break
            else:
                print(f'Instance State: {_state}')
                time.sleep(2)
                timeout += 1
        return instance_state


class SlackAWS:
    """Interact with AWS resources"""

    def __init__(self, slack_client, action, cmd_args):
        self.slack = slack_client
        self.action = action
        self.args = cmd_args
        self.instance_name = self.args.get('instance')
        self.dry_run = self.args.get('dry-run')
        self.aws = AWSClient()
        self.config = _get_config()['commands']['aws']
        self.replies = self.config['slack_replies']

    def __repr__(self):
        return f'AWS {self.option}\nARGS:\n{self.args}'

    def run_command(self):
        commands = {
            'stop': self.start_instance,
            'start': self.stop_instance,
            'restart': self.restart_instance,
            'reboot': self.reboot_instance
        }
        command = commands.get(self.action)
        command()

    def stop_instance(self) -> None:
        if self.aws.instance_exists(self.instance_name):
            if self.dry_run:
                instance_info = self.aws.get_instance_by_name(self.instance_name)
                msg = self.replies['restart']['dry_run'].format(self.instance_name, instance_info)
                self.slack.send_message(channel='#wtf', text=msg)
                return
            msg = self.replies['stop']['start'].format(self.instance_name)
            self.slack.send_message(channel='#wtf', text=msg)
            stop = self.aws.stop_instance(self.instance_name, dry_run=False)
            if self.aws.get_instance_state(self.instance_name) == 'stopped':
                msg = self.replies['stop']['complete'].format(self.instance_name, stop)
                self.slack.send_message(channel='#wtf', text=msg)

    def start_instance(self) -> None:
        if self.aws.instance_exists(self.instance_name):
            if self.dry_run:
                instance_info = self.aws.get_instance_by_name(self.instance_name)
                msg = self.replies['restart']['dry_run'].format(self.instance_name, instance_info)
                self.slack.send_message(channel='#wtf', text=msg)
                return
            msg = self.replies['start']['start'].format(self.instance_name)
            self.slack.send_message(channel='#wtf', text=msg)
            start = self.aws.start_instance(self.instance_name, dry_run=False)
            if self.aws.get_instance_state(self.instance_name) == 'running':
                msg = self.replies['start']['complete'].format(self.instance_name, start)
                self.slack.send_message(channel='#wtf', text=msg)

    def restart_instance(self) -> None:
        if self.aws.instance_exists(self.instance_name):
            if self.dry_run:
                instance_info = self.aws.get_instance_by_name(self.instance_name)
                msg = self.replies['restart']['dry_run'].format(self.instance_name, instance_info)
                self.slack.send_message(channel='#wtf', text=msg)
                return
            msg = self.replies['restart']['start'].format(self.instance_name)
            self.slack.send_message(channel='#wtf', text=msg)
            stop = self.aws.stop_instance(self.instance_name, dry_run=self.dry_run)
            if self.aws.get_instance_state(self.instance_name) == 'stopped':
                msg = self.replies['stop']['complete'].format(self.instance_name, stop)
                self.slack.send_message(channel='#wtf', text=msg)
            start = self.aws.start_instance(self.instance_name, dry_run=False)
            if self.aws.get_instance_state(self.instance_name) == 'running':
                msg = self.replies['start']['complete'].format(self.instance_name, start)
                self.slack.send_message(channel='#wtf', text=msg)

    def reboot_instance(self) -> None:
        if self.aws.instance_exists(self.instance_name):
            msg = self.replies['reboot']['start'].format(self.instance_name)
            self.slack.send_message(channel='#wtf', text=msg)
            self.aws.reboot_instance(self.instance_name, dry_run=self.dry_run)
            msg = self.replies['reboot']['complete'].format(self.instance_name)
            self.slack.send_message(channel='#wtf', text=msg)


def main() -> None:
    aws = AWSClient()
    i = aws.restart_instance('jke-control01')
    # i = aws.get_instance_state('jke-control01')
    print(i)


if __name__ == '__main__':
    main()
