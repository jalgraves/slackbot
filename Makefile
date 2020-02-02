.PHONY: all test clean build

test:
		python3 -m nose test/

compile:
		pip-compile requirements.in

build:
		docker build -t slackbot .

start:
		docker run --rm --name slackbot -e SLACK_API=${SLACK_API} slackbot

stop:
		docker rm -f slackbot || true

push:
		docker tag slackbot jalgraves/slackbot:latest
		docker push jalgraves/slackbot:latest

dist:
		python3 setup.py sdist bdist_wheel

install:
		pip3 install -U .

clean:
		rm -rf build/ || true
		rm -rf dist/ || true
		rm -rf *.egg-info/ || true