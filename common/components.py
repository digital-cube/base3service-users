from logging import getLogger

import models
from common.utils import set_user_session_to_store

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
