import jwt
import datetime
from tortoise import fields
from tortoise.models import Model


class Session(Model):

    class Meta:
        table = 'sessions'

    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField('users.AuthUser', source_field='id_user', index=True, related_name='sessions')
    created = fields.DatetimeField(null=False, auto_now_add=True)
    closed = fields.DatetimeField(null=True)
    active = fields.BooleanField(index=True, null=False, default=True)
    ttl = fields.IntField(null=True)

    @property
    async def token(self):
        await self.fetch_related('user')
        payload = {
            'id': str(self.id),
            'created': int(self.created.timestamp()),
            'expires': int((self.created + datetime.timedelta(seconds=self.ttl)).timestamp()) if self.ttl else None,
            'id_user': str(self.user.id),
            'permissions': self.user.role_flags
        }

        from base import registry
        encoded = jwt.encode(payload, registry.private_key(), algorithm='RS256')

        # this attribute will not be saved to DB
        return encoded.decode('ascii')

    async def serialize(self):

        await self.fetch_related('user')
        return {
            'id': self.id,
            'user': self.user.serialize(),
            'created': str(self.created),
            'closed': str(self.closed),
            'active': self.active,
            'ttl': self.ttl
        }
