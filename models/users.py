from tortoise.models import Model
from tortoise import fields

import base

from lookup.user_roles import USER, get_names


class Tenant(Model):
    class Meta:
        table = 'tenants'

    id = fields.UUIDField(pk=True)
    created = fields.DatetimeField(null=False, auto_now_add=True)
    name = fields.CharField(max_length=64, index=True, null=False, unique=True)
    users: fields.ReverseRelation['AuthUser']

    def serialize(self):
        return {
            'id': str(self.id),
            'created': str(self.created),
            'name': self.name
        }


class AuthUser(Model):

    class Meta:
        table = 'auth_users'

    id = fields.UUIDField(pk=True)
    created = fields.DatetimeField(null=False, auto_now_add=True)
    username = fields.CharField(max_length=64, index=True, null=False, unique=True)
    password = fields.CharField(max_length=64, null=False)
    role_flags = fields.IntField(index=True, null=False, default=USER)
    active = fields.BooleanField(index=True, null=False, default=True)
    scopes = fields.JSONField(null=True)
    tenant: fields.ForeignKeyRelation['Tenant'] = fields.ForeignKeyField(
        'users.Tenant', to_field='id', index=True, null=True, related_name='users',
        on_delete=fields.SET_NULL, source_field='id_tenant')
    user: fields.ReverseRelation['User']
    sessions: fields.ReverseRelation['Session']

    async def serialize(self, all_data=False, fields=None):

        await self.fetch_related('user', 'tenant')

        if fields:
            _data = {}
            if 'id' in fields:
                _data['id'] = str(self.id)
            if 'username' in fields:
                _data['username'] = str(self.username)
            if 'first_name' in fields:
                _data['first_name'] = self.user.first_name if self.user else None
            if 'last_name' in fields:
                _data['last_name'] = self.user.last_name if self.user else None
            if 'display_name' in fields:
                _data['display_name'] = await self.user.get_display_name() if self.user else None
            if 'profile_image' in fields:
                _data['profile_image'] = None

            return _data

        _data = {
            'id': str(self.id),
            'username': self.username,
            'first_name': self.user.first_name if self.user else None,
            'last_name': self.user.last_name if self.user else None,
            'display_name': await self.user.get_display_name() if self.user else None,
            'email': self.user.email if self.user else None,
            'active': self.active,
            'alarm_type': self.user.alarm_type if self.user else None,
            'notification_type': self.user.notification_type if self.user else None,
            'phone': self.user.phone if self.user else None,
            'role_flags': self.role_flags,
            'roles': get_names(self.role_flags),
            'scopes': self.scopes,
            'tenant': self.tenant.serialize() if self.tenant else None,
            'data': self.user.data,
            'profile_image': None
        }

        if all_data:
            _data.update({
                'role_flags': self.role_flags
            })

        return _data


class User(Model):

    class Meta:
        table = 'users'

    id = fields.UUIDField(pk=True)
    auth_user: fields.OneToOneRelation[AuthUser] = fields.OneToOneField('users.AuthUser', related_name='user', source_field='id_auth_user', to_field='id')
    first_name = fields.CharField(max_length=64, null=True)
    last_name = fields.CharField(max_length=64, null=True)
    email = fields.CharField(max_length=64, null=True)
    alarm_type = fields.IntField(default=0)
    notification_type = fields.IntField(default=0)
    phone = fields.CharField(max_length=64, null=True)
    data = fields.JSONField(null=True)

    async def get_display_name(self):

        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'

        if self.email:
            return self.email

        return self.auth_user.username
