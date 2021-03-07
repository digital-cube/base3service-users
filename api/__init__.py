import base

if base.config.conf['apptype'] == 'monolith':
    base.route.set('prefix', base.config.conf['services']['clients']['prefix'])
else:
    base.route.set('prefix', base.config.conf['prefix'])
