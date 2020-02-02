FROM alpine AS build

ENV K8S_VERSION=v1.17.2

RUN apk update && \
    apk add --no-cache \
        ca-certificates \
        build-base \
        curl

RUN curl -LO \
    https://storage.googleapis.com/kubernetes-release/release/${K8S_VERSION}/bin/linux/amd64/kubectl && \
    curl -sL https://istio.io/downloadIstioctl | sh -

FROM python:3.7-slim-buster
LABEL role=jke

ENV TINI_VERSION v0.18.0

RUN pip install -U pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt


COPY . /opt/app/

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini

COPY --from=build ./kubectl /
COPY --from=build /root/.istioctl/bin/istioctl /

RUN chmod +x /tini && \
    chmod +x kubectl && \
    mv kubectl /usr/bin/ && \
    chmod +x istioctl && \
    mv istioctl /usr/bin/ && \
    useradd --create-home appuser

# STOPSIGNAL SIGINT

USER appuser
ENTRYPOINT ["/tini", "-s", "--"]
WORKDIR /opt/app

CMD ["python", "slackbot/slackbot.py"]
