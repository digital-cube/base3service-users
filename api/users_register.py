import json
from logging import getLogger
from tortoise.transactions import in_transaction

import base
import models
from common.utils import format_password
from common.utils import set_user_session_to_store
from lookup.languages import EN
from lookup.languages import languages_list

log = getLogger('base')


@base.route(URI="/register")
class UsersRegisterHandler(base.Base):
    """
    Register an user.
    Registration is open for now, because of the VPN.
    """

    @base.api()
    async def post(self, user: models.users.AuthUser, user_data: models.users.User = None, active: bool = None):
        """
        Register user.
        Example API data: {
            "user": {
                "username": "user",
                "password": "123",
                "role_flags": 1
            },
            "user_data": {
                "first_name": "User",
                "last_name": "Test",
                "email": "user@test.loc",
                "notification_type": 1,
                "alarm_type": 1,
                "phone": "+33333333333"
            }
        }
        :param user: AuthUser object
        :param user_data:  User object
        :param active: should user be active or not. default value for AuthUser is True
        :return: {
                    'id': _users_id_,
                    'token': _jwt_authorization_token_
                }
        """
        async with in_transaction(base.config.conf['name']):
            user.username = user.username.lower().strip()

            if active is not None:
                user.active = active
            user.password = format_password(user.username, user.password)
            await user.save()

            if user_data is not None:
                user_data.auth_user = user
                if user_data.language not in languages_list:
                    user_data.language = EN
                await user_data.save()

            _session = models.session.Session(user=user)
            await _session.save()

            _user_data = await user.serialize(all_data=True)
            await set_user_session_to_store(_user_data, _session)

        token = await _session.token
        log.info(f'User withe username {user.username} successfully registered')

        return {'id': str(user.id), 'token': token}, base.http.status.CREATED
