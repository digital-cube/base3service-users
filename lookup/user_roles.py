"""
Define user roles
"""

USER = 2**0
ADMIN = 2**1
DEVELOPER = 2**2
SUPERUSER = 2**3

ADMINISTRATORS = ADMIN | SUPERUSER | DEVELOPER

names = {
    USER: 'USER',
    ADMIN: 'ADMIN',
    DEVELOPER: 'DEVELOPER',
    SUPERUSER: 'SUPERUSER'
}


names_list = [names[n] for n in names]


def get_names(role_flags):
    """
    Get a list of names for assigned roles
    :param role_flags: binary roles flags
    :return: list of roles names for binary role
    """

    return [names[_n] for _n in names if _n & role_flags]
