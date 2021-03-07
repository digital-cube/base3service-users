import base
from logging import getLogger

log = getLogger('base')


@base.route(URI="/about")
class AboutUsersHandler(base.Base):
    """
    Users service about API
    """

    @base.api()
    async def get(self):
        _ip_address = base.common.get_request_ip(self)
        log.info(f'About on users triggered from {_ip_address}')
        return {'service': 'users'}
