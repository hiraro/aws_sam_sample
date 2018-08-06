import logging
import pprint
import os
import sys
import json
import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    speech_text = event["Records"][0]["Sns"]["Message"]
    logger.info("speech_text: {}".format(speech_text))

    iot = boto3.client('iot-data')

    iot.publish(
        qos=0,
        topic="alexa_controller",
        payload=json.dumps({
            "speech_text": speech_text
        })
    )

    logger.info("Published.")
