import json
import logging
import re
import sys


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class SlackArgParse:
    """
    Parse Slack message bot command
    """
    def __init__(self, command_args, command_options, text):
        self.cmd_args = command_args
        self.cmd_options = command_options
        self.text = text
        self.args = self.parse_args(self.cmd_args, self.text)
        self.option = self.parse_option(self.text)
        # self.flags = self.parse_flags(self.cmd_args, self.text)

    def parse_args(self, cmd_args, text):
        """Parse command arguments"""
        args = {}
        search_args = {
            i: re.compile(f'(?<=-{i} ).*?(?= -\D|\Z)') for i in cmd_args.keys()
        }
        search_short_args = {
            i: re.compile(f'(?<=-{cmd_args[i]["short"]} ).*?(?= -\D|\Z)') for i in cmd_args.keys()
        }
        for k, v in search_args.items():
            if v.search(text):
                arg = v.search(text).group()
                args[k] = self.format_args(cmd_args[k]["type"], arg)
            elif search_short_args[k].search(text):
                arg = search_short_args[k].search(text).group()
                args[k] = self.format_args(cmd_args[k]["type"], arg)
            else:
                args[k] = False
        for k, v in cmd_args.items():
            if cmd_args[k]["type"] == "flag":
                if re.search(r'.*--{}.*'.format(k), text):
                    args[k] = True
        logging.info(f'SlackArgPargs - ARGS:\n{args}')
        return args

    def parse_flags(self, cmd_args, text):
        print(cmd_args)
        print(text)
        for k, v in cmd_args.items():
            if cmd_args[k]["type"] == "flag":
                if re.search(r'.*--{}.*'.format(k), text):
                    self.args[k] = True

    def parse_option(self, text) -> str:
        """Get option from text"""
        option = ''
        for i in self.cmd_options:
            match = re.match(r'.*( {} ).*'.format(i), text)
            if match:
                if match.groups()[0].strip() == i:
                    option = i
        return option

    @staticmethod
    def format_args(arg_type, text):
        """Format args based on type"""
        if arg_type == 'list':
            args_text = text.strip().split()
        elif arg_type == 'flag' and not text:
            args_text = True
        else:
            args_text = text.strip()
            if args_text.lower() == 'true':
                args_text = True
            elif args_text.lower() == 'false':
                args_text = False
        return args_text

    @staticmethod
    def format_message(message):
        """Format message"""
        message = message.strip()
        replace_chars = {
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&'
        }
        for k, v in replace_chars.items():
            message = message.replace(k, v)
        return message


if __name__ == '__main__':
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, 'config.json')) as f:
        config = json.load(f)
    cmd_args = config['commands']['aws']['valid_args']
    options = config['commands']['aws']['options']
    text = 'devbot aws restart -i jke-control01'
    parsed_args = SlackArgParse(cmd_args, options, text)
    print(f"OPTION: {parsed_args.option}")
    print(f"ARGS: {parsed_args.args}")
    # print(f"FLAGS: {parsed_args.flags}")
