from logging import getLogger

import base
import models
from common.components import UserBaseHandler
from lookup.scopes import names_list
from lookup.user_roles import ADMINISTRATORS

log = getLogger('base')


@base.route(URI="/users-scopes")
class UsersScopesHandler(base.Base):
    """
    Users scopes API
    """

    @base.auth(permissions=ADMINISTRATORS)
    @base.api()
    async def get(self):
        """
        Get available user's scopes - permission to access APIs
        :return: list o
        """

        _names = names_list[:]
        _names.sort()
        return {'scopes': _names}


@base.route(URI="/users-scopes/:id")
class UserScopesHandler(base.Base, UserBaseHandler):
    """
    User's scopes API
    """

    @base.auth(permissions=ADMINISTRATORS)
    @base.api()
    async def post(self, user: (models.AuthUser, 'id'), scopes: dict = None):
        """
        Set user's scopes - permission to access APIs
        :param user: AuthUser object
        :param scopes: dictionary {SCOPE_ID: SCOPE_PERMISSION}
        :return: list of
        """

        _changes = []

        if scopes is not None:
            if user.scopes is None:
                user.scopes = {}
            user.scopes = None if len(scopes.keys()) == 0 else scopes
            _changes.append('scopes')

        if _changes:
            await user.save()
            await self.update_user_session(user)
