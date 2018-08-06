#!/usr/bin/env python

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from polly import speech_with_polly
import logging
import pprint
import os
import time
import json
import boto3


CLIENT_ID = "AlexaController"
AWS_IOT_ENDPOINT = "xxxxxxxxxxxxx.iot.ap-northeast-1.amazonaws.com"
ROOT_CA_CERT = "./root-CA.crt"
DEV_CERT_PRIV = "./AlexaController.private.key"
DEV_CERT = "./AlexaController.cert.pem"
SUBSCRIPTION_TOPIC = "alexa_controller"


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


def on_online():
    logger.debug("online")

def on_offline():
    logger.debug("offline")

def on_alexa_control_message(client, userdata, message):
    try:
        payload = json.loads(message.payload)
        topic = message.topic

        logger.info("topic: {}".format(topic))
        logger.info("payload: {}".format(payload))

        speech_with_polly(payload["speech_text"])

        logger.info("done.")
    except:
        logging.exception("Caught Exception in on_alexa_control_message()")


if __name__ == '__main__':
    myMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
    myMQTTClient.configureEndpoint(
        AWS_IOT_ENDPOINT,
        8883
    )
    myMQTTClient.configureCredentials(
        ROOT_CA_CERT,
        DEV_CERT_PRIV,
        DEV_CERT
    )

    myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myMQTTClient.configureOfflinePublishQueueing(-1)
    myMQTTClient.configureDrainingFrequency(2)
    myMQTTClient.configureConnectDisconnectTimeout(10)
    myMQTTClient.configureMQTTOperationTimeout(5)

    myMQTTClient.onOnline = on_online
    myMQTTClient.onOffline = on_offline

    myMQTTClient.connect()
    time.sleep(2)

    logger.info("connexted to {} as {}".format(
        AWS_IOT_ENDPOINT, CLIENT_ID))

    myMQTTClient.subscribe(SUBSCRIPTION_TOPIC, 1, on_alexa_control_message)
    logger.info("subscribed topic: {}".format(
        SUBSCRIPTION_TOPIC))

    while True:
        time.sleep(1)
