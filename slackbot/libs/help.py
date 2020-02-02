import json
import os


def _get_config() -> dict:
    config_path = os.path.abspath('../')
    config_file = os.path.join(config_path, 'config.json')
    with open(config_file) as f:
        config = json.load(f)
    return config


class Help:
    """Interact with AWS resources"""

    def __init__(self, option=None):
        self.command = option

    def __repr__(self) -> str:
        return 'Slackbot Help'

    @property
    def config(self) -> dict:
        return _get_config()['help']

    def get_reply(self) -> str:
        if self.command:
            reply = self.config.get(self.command)
            if not reply:
                reply = f'_*Command `{self.command}` Not Found*_'
        else:
            reply = '\n'.join(self.config['all'])
        return reply


def main():
    _help = Help()
    print(_help.get_reply())


if __name__ == '__main__':
    main()
