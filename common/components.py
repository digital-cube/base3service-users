from logging import getLogger

import models
from common.utils import set_user_session_to_store
from lookup.user_roles import ADMINISTRATORS

log = getLogger('base')


class UserBaseHandler:

    async def update_user_session(self, user):
        """
        Find and update user's active shared session
        :param user:  AuthUser object
        :return: void
        """
        # update shared session if there is an active for the user
        _session = await models.session.Session.filter(user=user, active=True).get_or_none()
        if _session:
            _user_data = await user.serialize(all_data=True)
            await set_user_session_to_store(_user_data, _session)

    def get_fields(self, fields):

        if not self.user or 'role_flags' not in self.user or not bool(self.user['role_flags'] & ADMINISTRATORS):
            allowed_fields = ['id', 'username', 'first_name', 'last_name', 'display_name', 'profile_image']
            fields = allowed_fields if fields is None else [f for f in fields if f in allowed_fields]
            _u = self.user["id"] if self.user and "id" in self.user else self.user
            log.error(f'User {_u} is not permitted to access full users data, only: {fields}')
            return fields

        return None
