import json
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tilota.service import models
from tilota.core import utils

__all__ = (
    'GameInfoResource',
    'GameResource',
    'GameHistoryResource',
)


class ResourceAuthentication(BasicAuthentication):

    def is_authenticated(self, request, **kwargs):
        if request.user.is_authenticated():
            return True
        return super(ResourceAuthentication, self).is_authenticated(
                                                        request, **kwargs)


class OnlyUserContentAuthorization(DjangoAuthorization):

    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(
                user__pk=request.user.pk)
        return object_list.none()


class GameInfoResource(ModelResource):

    class Meta:
        queryset = models.GameInfo.objects.all()
        resource_name = 'game-info'
        allowed_methods = ['get']
        authentication = ResourceAuthentication()
        authorization = DjangoAuthorization()


class GameResource(ModelResource):

    class Meta:
        queryset = models.Game.objects.all()
        resource_name = 'game'
        allowed_methods = ['get', 'post']
        authentication = ResourceAuthentication()
        authorization = OnlyUserContentAuthorization()

    def hydrate(self, bundle):
        bundle.obj.user = bundle.request.user
        params = json.loads(bundle.request.raw_post_data)
        bundle.obj.info = models.GameInfo.objects.get(pk=params['info'])
        bundle.obj.dmtcp_id = utils.create_new_game(bundle.obj.info.cmd)
        return bundle


class GameHistoryResource(ModelResource):

    class Meta:
        queryset = models.GameHistory.objects.all()
        resource_name = 'game-history'
        allowed_methods = ['get', 'post']
        authentication = ResourceAuthentication()
        authorization = DjangoAuthorization()

    def hydrate(self, bundle):
        params = json.loads(bundle.request.raw_post_data)
        bundle.obj.game = models.Game.objects.get(pk=params['game'])
        bundle.obj.text = utils.play(
            bundle.obj.game.dmtcp_id, params['request'])
        return bundle
