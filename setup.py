from setuptools import setup, find_packages

VERSION = '0.0.01'

setup(
    name='jal_slackbot',
    version=VERSION,
    description='Python interactive Slack Chatbot',
    url='https://github.com:jalgraves/slackbot',
    author='Jonny Graves',
    author_email='jalgraves@gmail.com',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    install_requires=['slack'],
    include_package_data=True
)
