#!/usr/bin/env python3

from pydub import AudioSegment
from pydub.playback import play
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from contextlib import closing
import logging
import pprint
import os
import time
import json
import boto3
import fasteners


AWS_PROFILE = "develop"
POLLY_OUTPUT_FILE = "./polly.mp3"
VOICE = "Mizuki"


logger = logging.getLogger()

def speech_with_polly(text):
    with fasteners.InterProcessLock('./lockfile'):
        session = boto3.Session(profile_name=AWS_PROFILE)
        polly = session.client("polly")

        if os.path.isfile(POLLY_OUTPUT_FILE):
            os.remove(POLLY_OUTPUT_FILE)

        response = polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=VOICE
        )

        if "AudioStream" not in response:
            raise Exception("No AudoStream in response.")

        with closing(response["AudioStream"]) as stream:
            data = stream.read()
            fw = open(POLLY_OUTPUT_FILE, "wb")
            fw.write(data)
            fw.close()

            sound = AudioSegment.from_file(POLLY_OUTPUT_FILE, "mp3")
            play(sound)
