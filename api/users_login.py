import json
import datetime
from logging import getLogger
from tortoise.transactions import in_transaction

import base
import models
from common.utils import password_match, set_user_session_to_store

log = getLogger('base')


@base.route(URI="/session")
class UsersLoginHandler(base.Base):
    """
    Authenticate or an user.
    """

    @base.api()
    async def post(self, username: str, password: str):
        """
        Authenticate user.
        Example API data: {
            "username": "user",
            "password": "123"
            }
        :param username: user's username
        :param password:  user's password
        :return: {
                    'id': _users_id_,
                    'token': _jwt_authorization_token_
                }
        """
        async with in_transaction(base.config.conf['name']):
            username = username.lower().strip()
            user = await models.users.AuthUser.filter(username=username).get_or_none()
            if not user:
                log.error(f'User with username {user} do not exists')
                raise base.http.HttpErrorUnauthorized

            if not user.active:
                log.error(f'User {username} is not an active user and can not be authenticated')
                raise base.http.HttpErrorUnauthorized

            if not password_match(username, password, user.password):
                log.error(f'Password for user {username} -> {password} not match')
                raise base.http.HttpErrorUnauthorized

            _session = await models.session.Session.filter(user=user, active=True).get_or_none()
            if not _session:
                _session = models.session.Session(user=user)
                await _session.save()

            _user_data = await user.serialize(all_data=True)
            await set_user_session_to_store(_user_data, _session)

        token = await _session.token

        return {'id': str(user.id), 
                'token': token,
                'profile_image': 'digital-cube-logo.png'
                
                }, base.http.status.CREATED

    @base.auth()
    @base.api()
    async def get(self):
        """
        Check if the session is active.
        :return: dict - user's data
        """

        user = await models.users.AuthUser.get_or_none(id=self.id_user)
        if user:
            user_data = await user.serialize()
            
            user_data['profile_image'] = 'digital-cube-logo.png'
            
            return user_data
        raise base.http.HttpErrorUnauthorized

    @base.auth()
    @base.api()
    async def delete(self):
        """
        Close user's session
        :return: 204 success
        """

        async with in_transaction(base.config.conf['name']) as c:
            active_sessions = await models.session.Session.filter(user__id=self.id_user, active=True).all()

            _n = datetime.datetime.now()
            for session in active_sessions:
                session.active = False
                session.closed = _n
                await session.save()
                base.store.delete(str(session.id))
