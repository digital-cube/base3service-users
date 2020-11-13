from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

import datetime
import jwt

from base import orm
from base import common


class User(orm.BaseSql, orm.sql_base):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True)

    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    active = Column(Boolean, nullable=False, default=True)

    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)

    permission_flags = Column(Integer, nullable=False, default=1)

    def serialize(self, keys: list = ['id', 'username', 'email', 'permission_flags', 'first_name', 'last_name']):
        return super().serialize(keys, forbidden=['password'])


class Session(orm.BaseSql, orm.sql_base):
    __tablename__ = 'sessions'

    id = Column(UUID, primary_key=True)

    id_user = Column(ForeignKey(User.id), nullable=False, index=True)
    user = relationship(User, uselist=False, foreign_keys=[id_user])

    ttl = Column(Integer)
    active = Column(Boolean, index=True)
    closed = Column(DateTime)

    def __init__(self, user, ttl=None, active=True):
        super().__init__()
        self.user = user
        self.ttl = ttl
        self.active = active
        self.closed = None

        payload = {
            'id': self.id,
            'created': int(self.created.timestamp()),
            'expires': int((self.created + datetime.timedelta(seconds=self.ttl)).timestamp()) if self.ttl else None,
            'id_user': self.user.id,
            'permissions': self.user.permission_flags
        }

        from base import registry

        encoded = jwt.encode(payload, registry.private_key(), algorithm='RS256')

        # this attribute will not be saved to DB
        self.jwt = encoded.decode('ascii')


class ForgotPasswordId(orm.BaseSql, orm.sql_base):
    __tablename__ = 'forgot_password_ids'

    id_user = Column(ForeignKey(User.id), nullable=False, index=True)
    user = relationship(User, uselist=False, foreign_keys=[id_user])

    expired = Column(DateTime, nullable=True, default=None, index=True)

