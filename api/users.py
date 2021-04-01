import copy
from logging import getLogger

import base
import models
from common.components import UserBaseHandler
from common.utils import format_password
from lookup.scopes import names_list as scopes_names_list
from lookup.user_roles import names_list as roles_names_list
from lookup.user_roles import ADMINISTRATORS
import lookup.alarm_types as alarm_types
import lookup.notification_type as notification_types
from shared.src.ipc_helpers.documents import get_documents_for_an_instance

log = getLogger('base')


@base.route()
class UsersHandler(base.Base, UserBaseHandler):
    """
    Users API
    """

    @base.auth()
    @base.api()
    async def get(self, limit: int = 100, offset: int = 0, order_by: str = 'username', order_direction: str = 'asc',
                  fields: list = None, ids_users_csv: str = None):
        """
        Get the list of users
        :param limit: int - number of users to retrieve
        :param offset: int - number of first records to ignore
        :param order_by: str - order by field
        :param order_direction:  str - order direction
        :param fields: list - fields of a user object to send in the response
        :param ids_users_csv: str - csv of users ids to retrieve
        :return: list of users
        """

        fields = self.get_fields(fields)

        if order_by not in ['username', 'email', 'first_name', 'last_name']:
            log.error(f'Can not order users by {order_by}')
            return {'message': 'Invalid order key'}, base.http.status.BAD_REQUEST
        if order_by in ['email', 'first_name', 'last_name']:
            order_by = f'user__{order_by}'

        _filters = {'id__in': ids_users_csv.split(',')} if ids_users_csv else None
        if _filters:
            _users = await models.AuthUser.filter(**_filters).order_by(order_by).limit(limit).offset(offset)
        else:
            _users = await models.AuthUser.all().order_by(order_by).limit(limit).offset(offset)
        _users_ids = [str(u.id) for u in _users]
        _users = [await _u.serialize(fields=fields) for _u in _users]
        if _filters:
            _total = await models.AuthUser.filter(**_filters).count()
        else:
            _total = await models.AuthUser.all().count()
        _max_pages, _current_page = base.common.get_pages_counts(_total, limit, offset)

        _scopes = scopes_names_list[:]
        _scopes.sort()
        _roles = roles_names_list[:]
        _roles.sort()

        if _users_ids and len(_users) > 0 and 'profile_image' in _users[0] and 'id' in _users[0]:
            attachments, res = await get_documents_for_an_instance(self.request, 'user', ids_instances=_users_ids)
            if attachments and 'documents' in attachments:
                images_by_user_id = {}
                for a in attachments['documents']:
                    if 'id_instance' in a and str(a['id_instance']) in _users_ids:
                        _id_user = a['id_instance']
                        if _id_user not in images_by_user_id:
                            images_by_user_id[_id_user] = []
                        images_by_user_id[_id_user].append(a)

                for i in images_by_user_id:
                    images_by_user_id[i].sort(key=lambda _a: _a['created'], reverse=True)

                for _user in _users:
                    if _user['id'] in images_by_user_id:
                        _user['profile_image'] = images_by_user_id[_user['id']][0]      # only the last attached image # todo: this has to be fixed

        return {'users': _users,
                'summary': {'max_pages': _max_pages, 'current_page': _current_page, 'total_items': _total},
                'scopes': _scopes, 'role_flags': _roles}


@base.route(URI="/:id")
class UserHandler(base.Base, UserBaseHandler):
    """
    User API
    """

    @base.auth()
    @base.api()
    async def get(self, user: (models.AuthUser, 'id'), fields: list = None):
        """
        Get the user
        :param user: AuthUser object - user to retrieve
        :param fields: list - fields of a user object to send in the response
        :return: user's data
        """

        fields = self.get_fields(fields)
        _users_data = await user.serialize(fields=fields)
        return _users_data

    @base.auth(permissions=ADMINISTRATORS)
    @base.api()
    async def post(self, user: (models.AuthUser, 'id'), username: str, password: str):
        """
        Edit user's username and password
        :param username: str - user's username
        :param password: str - user's password
        :return: no content
        """
        username = username.strip()
        password = password.strip()

        user.username = username
        user.password = format_password(username, password)
        await user.save()
        await self.update_user_session(user)

    @base.auth(permissions=ADMINISTRATORS)
    @base.api()
    async def patch(self,
                    user: (models.AuthUser, 'id'), role_flags=None,
                    first_name: str = None, last_name: str = None,
                    email: str = None, alarm_type: int = None, notification_type: int = None, phone_number: str = None,
                    active: bool = None, last_used_application: str = None):
        """
        Edit user's data
        :param user: AuthUser object for db user to be changed
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

