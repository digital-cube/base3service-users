import json
from logging import getLogger

import bcrypt
import base
import models

log = getLogger('base')


def format_password(username, password):
    """
    Format user's password, salt it with the username.
    For changing the username there has to be a password provided
    :param username: user's username
    :param password: user's password
    :return:
        bcrypt-ed password if not in the test mode
        raw password if in the test mode
    """
    if 'test' in base.config.conf and base.config.conf['test']:
        return password

    return bcrypt.hashpw('{}{}'.format(username, password).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def password_match(username, password, db_password) -> bool:
    """
    Check if the user's provided password match the one in the database, with bcrypt
    :param username: provided by an user
    :param password: provided by an user
    :param db_password: user's bcrypt-ed password from the database
    :return: True if provided credentials match, otherwise False
    """

    if 'test' in base.config.conf and base.config.conf['test']:
        return password == db_password

    generated_password = '{}{}'.format(username, password).encode('utf-8')
    database_password = db_password.encode('utf-8')
    return database_password == bcrypt.hashpw(generated_password, database_password)


async def set_user_session_to_store(user_data: dict, session: models.session.Session) -> bool:
    """
    Set user's session to store
    :param user:  AuthUser
    :param session:
    :return: bool - success or not
    """
    try:
        _user_data = json.dumps(user_data, ensure_ascii=False)
        base.store.set(str(session.id), _user_data)
    except Exception as e:
        log.error(f'Error set user {user_data["id"] if "id" in user_data else user_data} session {session.id} to store: {e}')
        return False

    return True
