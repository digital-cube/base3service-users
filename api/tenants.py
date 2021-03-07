from logging import getLogger

import base
import models
from lookup.user_roles import SUPERUSER

log = getLogger('base')


@base.route(URI="/tenants")
class TenantsHandler(base.Base):
    """
    Tenants API
    """

    @base.auth(permissions=SUPERUSER)
    @base.api()
    async def get(self):
        _tenants = await models.Tenant.all()
        _tenants = [_t.serialize() for _t in _tenants]

        return {'tenants': _tenants}

    @base.auth(permissions=SUPERUSER)
    @base.api()
    async def post(self, tenant: models.Tenant):
        tenant.name = tenant.name.strip()
        await tenant.save()
        return {'id': str(tenant.id)}, base.http.status.CREATED


@base.route(URI="/tenants/:id")
class TenantHandler(base.Base):
    """
    Tenant API
    """

    @base.auth(permissions=SUPERUSER)
    @base.api()
    async def get(self, tenant: (models.Tenant, 'id')):
        return tenant.serialize()

    @base.auth(permissions=SUPERUSER)
    @base.api()
    async def put(self, tenant: (models.Tenant, 'id'), new_tenant: models.Tenant):
        new_tenant.name = new_tenant.name.strip()
        _changes = []
        if tenant.name != new_tenant.name:
            tenant.name = new_tenant.name
            _changes.append('name')
        if _changes:
            await tenant.save()
        return {'changes': _changes}

    @base.auth(permissions=SUPERUSER)
    @base.api()
    async def post(self, tenant: (models.Tenant, 'id'), user: (models.AuthUser, 'id')):
        user.tenant = tenant
        await user.save()
