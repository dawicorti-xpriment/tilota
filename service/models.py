from django.db import models
from django.contrib.auth.models import User

__all__ = ('GameInfo', 'Game', 'GameHistory')


class GameInfo(models.Model):
    name = models.CharField(max_length=32)
    cmd = models.CharField(max_length=32)
    first_request = models.CharField(max_length=256)


class Game(models.Model):
    user = models.ForeignKey(User)
    dmtcp_id = models.CharField(max_length=32, default=None)
    info = models.ForeignKey(GameInfo)


class GameHistory(models.Model):
    game = models.ForeignKey(Game)
    request = models.CharField(max_length=256)
    text = models.TextField()
