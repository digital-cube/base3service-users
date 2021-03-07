import os
import csv
import sys
import argparse
from tortoise import Tortoise, run_async
from tortoise.functions import Count

_current_path = os.path.dirname(__file__)
_root = os.path.abspath(os.path.join(_current_path, '../../'))
sys.path.append(_root)

import models
from base import config
from lookup import user_roles
from common.utils import format_password

USERS_FILE = 'openlight_users.csv'

PHONES = {
    'stefan.mutschlechner@asmmerano.it': {'name': 'Stefan', 'number': '+393481229852'},
    'sergio.raffa@asmmerano.it': {'name': 'Sergio', 'number': '+393426522011'},
    'roberto.zampolli@asmmerano.it': {'name': 'Roberto', 'number': '+393426330930'},
    'martin.theiner@asmmerano.it': {'name': 'Martin', 'number': '+393421897770'},
    'norbert.pixner@asmmerano.it': {'name': 'Norbert', 'number': '+393426420919'}
}


async def prepare_users(args):
    """
    Exported data:
        username, password, role_flags, first_name, last_name, email, alarm_type, notification_type
    :return:  void
    """

    # export to args.file
    _file = f'{_current_path}/{args.file}'
    os.system(
        f'''psql -U openlight openlight -c "copy (select username, password, role_flags, first_name, last_name, email, alarm_type, notification_type from auth_users au join users u on au.id = u.id where active and au.id not in ('u00000Hdy3')) to stdout with CSV" > {_file}'''
    )


async def seed_users(args):

    config.load_from_yaml(f'{_root}/config/config.{os.getenv("ENVIRONMENT", "local")}.yaml')
    await Tortoise.init(
        config=config.tortoise_config()
    )

    _exists = await models.users.AuthUser.all().count()
    if _exists:
        # do not add seed
        return

    _file = f'{_current_path}/{args.file}'
    with open(_file) as f:
        csv_reader = csv.reader(f)
        for csv_user in csv_reader:
            print(csv_user)

            auth_user = models.AuthUser()
            auth_user.username = csv_user[0]
            auth_user.password = csv_user[1]
            auth_user.role_flags = int(csv_user[2])
            # on new users platform user's roles are changed ADMIN -> SUPERUSER
            if auth_user.role_flags == user_roles.ADMIN and auth_user.username != 'admin':
                auth_user.role_flags = user_roles.SUPERUSER
            if auth_user.username == 'roberto.zampolli@asmmerano.it':
                auth_user.role_flags = user_roles.ADMIN

            auth_user.scopes = {'OPENWASTE': 3, 'OPENLIGHT': 3}
            await auth_user.save()

            user = models.User()
            user.auth_user = auth_user
            user.first_name = csv_user[3]
            user.last_name = csv_user[4]
            user.email = csv_user[5]
            user.alarm_type = int(csv_user[6])
            user.notification_type = int(csv_user[7])
            user.phone = PHONES[auth_user.username]['number'] if auth_user.username in PHONES else None
            await user.save()


async def main(args):
    if args.prepare:
        await prepare_users(args)

    await seed_users(args)


def pars_arguments():
    parser = argparse.ArgumentParser(
        description='Seed users from openlight or prepare user data from openlight for seed')
    parser.add_argument('-p', '--prepare', help='Prepare users from openlight in csv', action='store_true')
    parser.add_argument('-f', '--file', help='Input/Output file', default=USERS_FILE)

    return parser.parse_args()


if __name__ == '__main__':
    args = pars_arguments()
    run_async(main(args))
