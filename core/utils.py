# -*- coding: utf-8 *-*
import os
import uuid
import re
import logging
from tilota import settings
from tilota.core.console import Console


def get_logger():
    logger = logging.getLogger('Utils')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(os.path.join(
        os.path.dirname(__file__), 'utils.log'))
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)-8s %(name)-8s %(message)s'))
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def create_new_game(game_cmd):
    folder = os.path.abspath(
        os.path.join(
            settings.CACHE_PATH,
            str(uuid.uuid1())
        )
    )
    try:
        os.makedirs(folder)
    except:
        pass
    game = Console('dmtcp_checkpoint -q -q' % game_cmd, cwd=folder)
    Console('dmtcp_command -bc', cwd=folder)
    checkpoint_path = None
    for file_name in os.listdir(folder):
        if file_name.startswith('ckpt_'):
            checkpoint_path = os.path.join(folder, file_name)
            break
    return checkpoint_path


def play(checkpoint_path, cmd):
    folder, checkpoint_name = os.path.split(checkpoint_path)
    game = Console('dmtcp_restart -q -q %s' % checkpoint_name, cwd=folder)
    answer = game.cmd(cmd)
    formated_answer = ''
    for line in answer.split('\n'):
        if not re.compile('^' + cmd + '$').match(line):
            formated_answer += line
    os.system('dmtcp_command -bc')
    return formated_answer
