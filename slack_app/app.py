import logging
import datetime
import pprint
import os
import json
import hmac
import urllib
import hashlib
import boto3


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def __generate_hmac_signature(timestamp, body):
    secretkey = os.environ['SLACK_API_SIGNING_SECRET']
    secretkey_bytes = bytes(secretkey, 'UTF-8')

    message = "v0:{}:{}".format(timestamp, body)
    message_bytes = bytes(message, 'UTF-8')
    return hmac.new(secretkey_bytes, message_bytes, hashlib.sha256).hexdigest()


def is_valid_event(event):
    if "X-Slack-Request-Timestamp" not in event["headers"] \
            or "X-Slack-Signature" not in event["headers"]:
        return False

    request_timestamp = event["headers"]["X-Slack-Request-Timestamp"]
    now_timestamp = int(datetime.datetime.now().timestamp())

    if abs(request_timestamp - now_timestamp) > (60 * 5):
        return False

    expected_hash = __generate_hmac_signature(
        event["headers"]["X-Slack-Request-Timestamp"],
        event["body"]
    )

    expected = "v0={}".format(expected_hash)
    actual = event["headers"]["X-Slack-Signature"]

    logger.debug("Expected HMAC signature: {}".format(expected))
    logger.debug("Actual HMAC signature: {}".format(actual))

    return hmac.compare_digest(expected_hash, actual)

def on_slack_command(cmd_arg):
    client = boto3.client('sns')

    response = client.publish(
        TopicArn=os.environ['POLLY_TASK_TOPIC_ARN'],
        Message=cmd_arg
    )

    logger.info(response)

def lambda_handler(event, context):
    if not is_valid_event(event):
        return {
            "isBase64Encoded": False,
            "statusCode": 403,
            "body": "おいこら誰だてめぇ"
        }

    logger.info("おｋ")

    payload = urllib.parse.parse_qs(event["body"])
    logger.debug(pprint.pformat(payload, indent=4))

    cmd_arg = os.environ['ALEXA_COMMAND_PREFIX'] + " ".join(payload["text"])
    logger.info("cmd arg: {}".format(cmd_arg))

    on_slack_command(cmd_arg)

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": cmd_arg
    }
