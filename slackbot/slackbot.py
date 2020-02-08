import os
import json
import logging
import sys
import time

import slack

from libs.slackparse import SlackArgParse
from libs.aws import SlackAWS
from libs.k8s import K8s
from libs.help import Help


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def _config() -> dict:
    current_dir = os.path.realpath(__file__)
    file_path = os.path.dirname(current_dir)
    config_path = os.path.join(file_path, 'config.json')
    with open(config_path) as f:
        config = json.load(f)
    return config


def _bot_check(text: str) -> str:
    botnames = CONFIG['botnames']
    bot = False
    if text.split()[0] in botnames:
        bot = _check_command(text.split()[1:])
        logging.info(f'BOT: {bot}')
    return bot


def _check_command(args: list) -> str:
    command = ''
    bot_commands = CONFIG['commands'].keys()
    if args[0] in bot_commands:
        command = args[0]
        logging.info(f'COMMAND: {command}')
    return command


CONFIG = _config()


class BotCommand:
    """Run a bot command issued from Slack"""
    def __init__(self, slack_client, command, config, data):
        self.client = slack_client
        self.command = command
        self.config = config
        self.data = data
        self.parsed_args = SlackArgParse(self.config['valid_args'], self.config['options'], self.data['text'])
        self.args = self.parsed_args.args
        self.option = self.parsed_args.option
        logging.info(f'OPTION: {self.option}')
        logging.info(f'ARGS: {self.args}')

    def run_command(self):
        commands = {
            'help': Help,
            'k8s': K8s,
            'aws': SlackAWS,
            'stop': self._stop_bot
        }
        command = commands.get(self.command)
        if command:
            cmd = command(self.option, self.args)
            logging.info(f'CMD: {cmd}')
            self.send_message(self.data['channel'], f'```{cmd}```')

    def _stop_bot(self):
        msg = ">*Shutting Down Bot*"
        self.send_message(self.data['channel'], msg)
        sys.exit(0)

    def send_message(self, channel: str, text: str) -> dict:
        return self.client.chat_postMessage(channel=channel, text=text)

    def add_reaction(self, channel: str, timestamp: str, emoji: str) -> dict:
        return self.client.reactions_add(channel=channel, timestamp=timestamp, name=emoji)

    def delete_reaction(self, channel: str, timestamp: str, emoji: str) -> dict:
        return self.client.reactions_remove(channel=channel, timestamp=timestamp, name=emoji)

    def update_reaction(self, msg, reaction):
        self.delete_reaction(msg['channel'], msg['ts'], emoji='spinning')
        if reaction == 'success':
            self.add_reaction(msg['channel'], msg['ts'], emoji='nhl_bos')
        else:
            self.add_reaction(msg['channel'], msg['ts'], emoji='nba_bos')


class SlackBot:
    """Interactive Slack Chatbot"""

    def __init__(self, api_key):
        self.client = slack.RTMClient(token=api_key)

    @staticmethod
    @slack.RTMClient.run_on(event='message')
    def message_data(**payload):
        data = payload['data']
        client = payload['web_client']
        if data.get('text'):
            bot_command = _bot_check(data['text'])
            logging.info(f'BOT COMMAND: {bot_command}')
            if bot_command:
                config = CONFIG['commands'][bot_command]
                command = BotCommand(client, bot_command, config, data)
                command.run_command()
            else:
                logging.info(f'NO BOT COMMAND')

    @staticmethod
    @slack.RTMClient.run_on(event='open')
    def team_data(**payload):
        logging.info(payload)

    def start_bot(self):
        self.client.start()


def slackbot():
    slackbot = SlackBot(os.environ.get('SLACK_API'))
    slackbot.start_bot()


if __name__ == '__main__':
    slackbot()
