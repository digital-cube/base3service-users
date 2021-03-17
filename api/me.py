import copy
from logging import getLogger

import base
import models
from common.components import UserBaseHandler
from common.utils import format_password
import lookup.alarm_types as alarm_types
import lookup.notification_type as notification_types

log = getLogger('base')


@base.route(URI="/me")
class MeHandler(base.Base, UserBaseHandler):
    """
    User's API
    """

    @base.auth()
    @base.api()
    async def get(self):
        """
        Get the user
        :return: logged user's data
        """
        user = await models.AuthUser.filter(id=self.id_user).get_or_none()
        if not user:
            raise base.http.HttpErrorNotFound

        _users_data = await user.serialize()
        return _users_data

    @base.auth()
    @base.api()
    async def post(self, username: str, password: str):
        """
        Edit logged user's username and password
        :param username: str - user's username
        :param password: str - user's password
        :return: no content
        """
        username = username.strip()
        password = password.strip()

        user = await models.AuthUser.filter(id=self.id_user).get_or_none()
        if not user:
            raise base.http.HttpErrorNotFound

        user.username = username
        user.password = format_password(username, password)
        await user.save()
        await self.update_user_session(user)

    @base.auth()
    @base.api()
    async def patch(self, role_flags=None, first_name: str = None, last_name: str = None, email: str = None,
                    alarm_type: int = None, notification_type: int = None, phone_number: str = None,
                    active: bool = None, last_used_application: str = None):
        """
        Edit user's data
        :param role_flags: int - user's role flags
        :param first_name: user's first name
        :param last_name: user's last name
        :param email: user's email
        :param alarm_type: user's alarm type
        :param notification_type: user's notifications types
        :param phone_number: user's phone number
        :param active: user's active status
        :return: list of changes
        """

        _changes = []

        user = await models.AuthUser.filter(id=self.id_user).get_or_none()
        if not user:
            raise base.http.HttpErrorNotFound

        user_data = await models.User.filter(auth_user=user).get_or_none()

        if role_flags is not None and user.role_flags != role_flags:
            user.role_flags = role_flags
            _changes.append('role_flags')

        if first_name is not None and user_data.first_name != first_name:
            user_data.first_name = first_name
            _changes.append('first_name')

        if last_name is not None and user_data.last_name != last_name:
            user_data.last_name = last_name
            _changes.append('last_name')

        if email is not None and user_data.email != email:
            user_data.email = email
            _changes.append('email')

        if alarm_type is not None and user_data.alarm_type != alarm_type:
            if not bool(alarm_type & alarm_types.ALL):
                log.error(f'Alarm type {alarm_type} not exists')
                return {'message': 'Invalid alarm type'}, base.http.status.BAD_REQUEST

            user_data.alarm_type = alarm_type
            _changes.append('alarm_type')

        if notification_type is not None and user_data.notification_type != notification_type:
            if not bool(notification_type & notification_types.ALL):
                log.error(f'Notification type {notification_type} not exists')
                return {'message': 'Invalid notification type'}, base.http.status.BAD_REQUEST

            user_data.notification_type = notification_type
            _changes.append('notification_type')

        if phone_number is not None and user_data.phone != phone_number:
            user_data.phone = phone_number
            _changes.append('phone_number')

        if active is not None and user.active != active:
            user.active = active
            _changes.append('active')

        if last_used_application is not None:
            _user_data = copy.deepcopy(user_data.data) if user_data.data else {}
            if 'last_used_application' not in _user_data or _user_data['last_used_application'] != last_used_application:
                _user_data['last_used_application'] = last_used_application
                user_data.data = _user_data
                _changes.append('last_used_application')

        if _changes:
            await user_data.save()
            await user.save()
            await self.update_user_session(user)

        return {'changes': _changes}

