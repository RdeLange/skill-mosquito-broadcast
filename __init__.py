"""
skill mosquito-broadcast
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from mycroft import intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
import paho.mqtt.client as mqtt
import re
import time
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG
from os.path import dirname, join
from mycroft.util import play_mp3


__author__ = 'rdl'

try:
    client
    LOG.info('Client exist')
    client.loop_stop()
    client.disconnect()
    LOG.info('Stopped old client loop')
except NameError:
    client = mqtt.Client()
    LOG.info('Client created')


class MosquitoBroadcast(MycroftSkill):
    def __init__(self):
        super(MosquitoBroadcast, self).__init__(name='MosquitoBroadcast')
        self.host = None
        self.port = None
        self.topic = None
        self.uuid = None
        self.last_message = None
        self.splitRegex = None
        self.retainFirst = None
        self.retainLast = None
        self.loop_succeeded = False
        self.lastbroadcastsend = None
        self.process = None

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic)
        if rc == 0:
            LOG.info('Connected to ' + self.topic)
        else:
            LOG.error('Connection to ' + self.topic +
                      ' failed, error code ' + rc)

    def on_message(self, client, userdata, msg):
        try:
            m = msg.payload.decode('utf-8')

            if self.splitRegex:
                m = re.sub(self.splitRegex, lambda x:
                    x.group(0)[0:int(self.retainFirst)] +
                    ' ' + x.group(0)[int(self.retainLast):], m)
            if (self.lastbroadcastsend != m):
                self.process = play_mp3(join(dirname(__file__), "broadcast.mp3"))
                time.sleep(4)
                self.speak(m)
                self.last_message = m

        except Exception as e:
            LOG.error('Error: {0}'.format(e))

    def initialize(self):
        self.settings.set_changed_callback(self.on_websettings_changed)
        self.on_websettings_changed()
        self.loop_succeeded = False
        if not self.intro:
           self.IntroductionMessage = ""
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        if self._is_setup:
            self.mqtt_init()

    def on_websettings_changed(self):  # called when updating mycroft home page
        self._is_setup = False
        self.host = self.settings.get('host',"127.0.0.1")
        self.port = int(self.settings.get('port',1884))
        self.topic = self.settings.get('topic',"Mycroft/broadcast")
        self.splitRegex = self.settings.get('splitRegex')
        self.retainFirst = self.settings.get('retainFirst')
        self.retainLast = self.settings.get('retainLast')
        self.intro = self.settings.get('Intro')
        self.IntroductionMessage = self.settings.get('IntroductionMessage')
        self.last_message = 'There is no last broadcast'
        try:
            client
            LOG.info('Client exist')
            client.loop_stop()
            client.disconnect()
            LOG.info('Stopped old client loop')
        except NameError:
            client = mqtt.Client()
            LOG.info('Client re-created')
        LOG.info("Websettings Changed! " + self.host + ", " + str(self.port))
        self.mqtt_init()
        self._is_setup = True

    def mqtt_init(self):  # initializes the MQTT configuration and subscribes to its own topic
        self.loop_succeeded = False
        try:
            LOG.info("Connecting to host: " + self.host + ", on port: " + str(self.port))
            client.connect_async(self.host, self.port, 60)
            client.loop_start()
            self.loop_succeeded = True
            LOG.info("MQTT Loop Started Successfully")
        except Exception as e:
            LOG.error('Error: {0}'.format(e))

    @intent_file_handler('RepeatLastBroadcast.intent')
    def repeat_last_message_intent(self):
        self.speak(self.last_message)

        if not self.loop_succeeded:
            self.speak_dialog('not_configured')

    @intent_handler(IntentBuilder("").require("Broadcast").require("Words"))
    def broadcastmessage(self, message):
        """
            Broadcast the utterance to all other devices with the Mosquito Broadcast Skill installed.
        """
        # Remove everything up to the broadcast keyword and publish that on the mqtttopic
        utterance = message.data.get('utterance')
        repeat = re.sub('^.*?' + message.data['Broadcast'], '', utterance)
        #self.speak("Your message is broadcasted to all other devices.")
        self.speak_dialog('send_broadcast')

        client.publish(self.topic, self.IntroductionMessage+ " "+repeat.strip())
        self.lastbroadcastsend = self.IntroductionMessage+ " "+repeat.strip()

    def stop(self):
        pass


def create_skill():
    return MosquitoBroadcast()
