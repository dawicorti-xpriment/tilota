#!/usr/bin/python
# -*- coding: utf-8 *-*
import daemon
from tilota import settings
from tilota.core.console import Console
import zmq
import re
import os
import logging


class Daemon(object):

    def __init__(self, fake=False):
        self._fake = fake

    def initialize(self):
        pass

    def run(self):
        pass

    def start(self):
        if self._fake:
            self.initialize()
            self.run()
        else:
            with daemon.DaemonContext():
                self.initialize()
                self.run()


class TilotaDaemon(Daemon):

    def initialize(self):
        os.environ['DMTCP_CHECKPOINT_DIR'] = settings.CACHE_PATH
        os.chdir(settings.CACHE_PATH)
        self.logger = logging.getLogger('Tilota Daemon')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(os.path.join(
            os.path.dirname(__file__), 'tilotad.log'))
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)-8s %(name)-8s %(message)s'))
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)
        self.logger.debug('Starting Tilota Daemon')
        self._coordinator = Console('dmtcp_coordinator')
        self._coordinator.read()
        self._inbox = zmq.Socket(zmq.Context(), zmq.PULL)
        self._inbox.bind(settings.DAEMON_INBOX)
        self.CALLBACKS = {
            'get_game_id': self.get_game_id,
            'save_checkpoints': self.save_checkpoints,
        }

    def _dispatch(self, message):
        self.logger.debug('Dispatching message %s', str(message))
        message_name = message.get('name', None)
        if message_name in self.CALLBACKS:
            self.CALLBACKS[message_name](message)

    def reply(self, input_message, output_message):
        reply_ipc = input_message.get('reply_ipc', None)
        if reply_ipc:
            outbox = zmq.Socket(zmq.Context(), zmq.PUSH)
            outbox.connect(reply_ipc)
            outbox.send_json(output_message)
            self.logger.debug(
                'Replying %s to message %s',
                str(output_message), str(input_message)
            )

    def save_checkpoints(self, message):
        self._coordinator.cmd('c')
        self.reply(message, {})

    def get_game_id(self, message):
        self.logger.debug('Get message id from %s', str(message))
        if not message.get('pid', None):
            raise ValueError
        response = self._coordinator.cmd('l')
        self.logger.debug('Response to coordinator list : %s', response)
        search_result = re.compile(
            '[0-9]+\, [\w]+\[%d\]\@[\w]+\,' \
            ' ([\w\-]+)\, RUNNING' % message['pid']
        ).search(response)
        game_id = None
        if search_result:
            game_id = search_result.group(1)
        self.logger.debug('Game id found : %s', str(game_id))
        self.reply(message, {'game_id': game_id})

    def run(self):
        while True:
            message = self._inbox.recv_json()
            self._dispatch(message)


if __name__ == '__main__':
    import psutil
    for proc in psutil.process_iter():
        if proc.name == 'tilotad.py' and proc.pid != os.getpid() \
                                     or proc.name == 'dmtcp_coordinator':
            proc.kill()
    TilotaDaemon().start()
