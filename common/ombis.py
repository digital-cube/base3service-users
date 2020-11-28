import json
from base import config, http

from tornado.httpclient import AsyncHTTPClient

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


async def get(url: str, params: dict = {}):
    if '?' in url:
        raise http.HttpInternalServerError(id_message='INVALID_URL',
                                           message='Invalid URL, use url and params separated',
                                           url=url)

    try:
        ocfg = config.conf['ombis']
        host = ocfg['host']
        port = ocfg['port']
        user = ocfg['user']
        password = ocfg['password']
    except:
        ocfg = None

    if not ocfg:
        raise http.HttpInternalServerError(id_message='INVALID_CONFIGURATION',
                                           message='Ombis not proprely configured')

    client = AsyncHTTPClient()

    _url = f'http://{host}:{port}{url}?json'.strip()

    lst = []
    for key in params.keys():
        if params[key] not in ('', None):
            lst.append(f'{key}={params[key]}')

    params = '&'.join(lst)
    if params:
        _url += '&'+params

    try:
        res = await client.fetch(_url, auth_username=user, auth_password=password, auth_mode='digest')
    except BaseException as e:
        print('ombis get exception', e)
        print('url', url)
        print(e)
        return None

    data = json.loads(res.body.decode('utf-8'))
    return data
