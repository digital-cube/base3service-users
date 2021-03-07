import os
import sys
from faker import Faker
from tortoise import Tortoise, run_async
from tortoise.functions import Count

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(_root)

import models
from base import config
from lookup import user_roles
from common.utils import format_password


async def main():

    f = Faker()
    config.load_from_yaml(f'{_root}/config/config.{os.getenv("ENVIRONMENT", "local")}.yaml')
    await Tortoise.init(
        config=config.tortoise_config()
    )

    _exists = await models.users.AuthUser.all().count()
    if _exists:
        # do not add seed
        return

    _roles = [
        (user_roles.USER, 10),
        (user_roles.ADMIN, 5),
        (user_roles.DEVELOPER, 2),
        (user_roles.SUPERUSER, 2),
    ]
    for role in _roles:
        for _ in range(role[1]):
            auth_user = models.AuthUser()
            auth_user.username = f.user_name()
            auth_user.password = format_password(auth_user.username, '123')
            auth_user.role_flags = role[0]
            auth_user.scopes = {'OPENWASTE': 3, 'OPENLIGHT': 3}
            await auth_user.save()

            user = models.User()
            user.auth_user = auth_user
            user.first_name = f.first_name()
            user.last_name = f.last_name()
            user.email = f.email()
            user.alarm_type = 1
            user.notification_type = 1
            user.phone = f.phone_number()
            await user.save()


if __name__ == '__main__':

    run_async(main())