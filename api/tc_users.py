import os
import base
from base import paginate, http

import orm.models as models
import uuid

import json
from tornado.httpclient import AsyncHTTPClient

if base.config.conf['apptype'] == 'monolith':
    base.route.set('prefix', base.config.conf['services']['users']['prefix'])
else:
    base.route.set('prefix', base.config.conf['prefix'])

import orm.mysql_portal as one_portal_orm

from common import ombis


@base.route('/info')
class GeneralInfo(base.Base):

    @base.api()
    async def get(self):
        return {'environment': os.getenv('TC_ENVIRONMENT', 'undefined - setup TC_ENVIRONMENT variable'),
                'service-version': '0.1.0'}


@base.route(URI="/by-org-units")
class UserHandlerByUnits(base.Base):

    @base.auth()
    @base.api()
    async def get(self):
        res = {}

        for u in self.orm_session.query(models.User).order_by(models.User.first_name,
                                                              models.User.last_name,
                                                              models.User.username):

            if u.org_unit not in res:
                res[u.org_unit] = []

            res[u.org_unit].append(u.serialize(['id', 'first_name', 'last_name', 'profile_picture']))

        org_units = list(res.keys())
        org_units = [x for x in org_units if x]
        org_units.sort()

        sorted = [x for x in org_units if x not in ('Other', None)]

        if len(sorted) != len(org_units):
            sorted.append('Other')

        rrr = {}
        for ou in sorted:
            rrr[ou] = res[ou]

        return rrr


@base.route("/all")
class AllUserHandler(base.Base):

    @base.auth()
    @base.api()
    async def get(self, mapped_by=None):
        if not mapped_by:
            return [u.serialize(keys=["id", "id_ombis"]) for u in self.orm_session.query(models.User).all()]

        if mapped_by == 'id_ombis':
            res = {u.id_ombis: u.id for u in self.orm_session.query(models.User).
                filter(models.User.id_ombis != None).all()}

            return res

        raise http.HttpInvalidParam({"message": f"invalid mapped by parameter {mapped_by}"})


@base.route(URI="/all-with-details-mapped-by-ombis")
class AllDetailsUserHandler(base.Base):

    @base.auth()
    @base.api()
    async def get(self):
        res = {u.id_ombis: u.serialize(['id', 'first_name', 'last_name', 'org_unit', 'email', 'profile_picture']) for u
               in self.orm_session.query(models.User). \
                   filter(models.User.id_ombis != None).all()}

        return res


@base.route(URI="/info/by_uids")
class UsersInfoHandler(base.Base):

    @base.auth()
    @base.api()
    async def get(self, csv_users: str):
        id_users = csv_users.split(',')
        return {
            user.id: user.serialize(['id', 'profile_picture', 'first_name', 'last_name', 'org_unit']) for user in
            self.orm_session.query(models.User).filter(models.User.id.in_(id_users))
        }


@base.route(URI=['/ombis-users-sync', '/fetch'])  # TODO: Remove /ombis-users-sync', i prebaci na GET!
class OmbisUsersSyncHandler(base.Base):

    @base.api()
    async def patch(self, ombis_id_users: str = 'all'):

        params = {}

        if ombis_id_users != 'all':
            ombis_id_users = ','.join([str(int(x)) for x in ombis_id_users.split(',')])
            params['filter'] = f'in(ID,{ombis_id_users})'

        params['fields'] = 'ID,Name,FullName'

        ombis_url = f'/rest/web/00000001/user'

        res = await ombis.get(ombis_url, params)

        res = {
            user['Fields']['ID']: {
                'username': user['Fields']['Name'],
                'first_name': user['Fields']['FullName'].split(' ')[0],
                'last_name': user['Fields']['FullName'].split(' ')[-1]
            }
            for user in res['Data']
        }
        ombis_ids = [int(i) for i in res.keys()]

        users = {user.id_ombis for user in
                 self.orm_session.query(models.User).filter(models.User.id_ombis.in_(ombis_ids)).all()}

        ombis_url = f'/rest/web/00000001/mitarbeiter'

        params = {'filter': 'eq(Gesperrt,0)',
                  'fields': 'UserID,Suchbegriff',
                  'refs': 'Abteilung(fields=DisplayName)'}

        org_units = await ombis.get(ombis_url, params)
        org_units = {
            str(user['Fields']['UserID']): user['References']['Abteilung']['Fields']['DisplayName']
            for user in org_units['Data']
        }

        commit = False
        added, skipped = 0, 0

        prepare4absences = []

        for s_id_ombis in res.keys():
            id_ombis = int(s_id_ombis)
            if s_id_ombis in users:
                skipped += 1
                continue

            added += 1

            u = res[s_id_ombis]
            usr = models.User(username=u['username'],
                              password=str(uuid.uuid4()),
                              role_flags=0,
                              first_name=u['first_name'],
                              last_name=u['last_name'],
                              org_unit=org_units[s_id_ombis] if s_id_ombis in org_units else 'Other',
                              id_ombis=id_ombis
                              )
            self.orm_session.add(usr)
            commit = True

            prepare4absences.append(usr.id)

        if commit:
            self.orm_session.commit()

        ires = await base.ipc.call(self.request, 'absences', 'POST', '/sync', body={
            'user_ids': prepare4absences
        })

        return {'added': added, 'skipped': skipped}


@base.route(URI='/one-portal-users')
class CopyAllUsersFromOnePortal(base.Base):

    @base.auth()
    @base.api()
    async def get(self):
        return {
            user.username: user.id for user in self.orm_session.query(models.User).all()
        }

    @base.api()
    async def post(self):
        added = 0
        with one_portal_orm.telmekom_orm_session() as session:
            q = session.execute(
                "select a.id, a.username, a.role_flags, a.password, u.client_name, u.first_name, u.last_name, u.profile_picture, u.org_unit, u.id_ombis from auth_users a left join users u on a.id=u.id where a.active=1 and a.role_flags & 253956!=0")
            for au in q:
                id_one_user = au[0]
                _email = au[1]
                _one_portal_roleflags = au[2]

                _one_portal_crypted_password = au[3]

                _client_name = au[4]
                _first_name = au[5]
                _last_name = au[6]
                _profile_picture = au[7]
                _org_unit = au[8]
                _id_ombis = au[9]

                portal_data = {'id': id_one_user,
                               'email': _email,
                               'roleflags': _one_portal_roleflags,
                               'client_name': _client_name,
                               'first_name': _first_name,
                               'last_name': _last_name,
                               'profile_picture': _profile_picture,
                               'org_unit': _org_unit,
                               'id_ombis': _id_ombis
                               }

                user = models.User(username=portal_data['email'],
                                   password='123',
                                   role_flags=0,
                                   first_name=portal_data['first_name'],
                                   last_name=portal_data['last_name'],
                                   email=portal_data['email'],
                                   org_unit=portal_data['org_unit'],
                                   id_ombis=_id_ombis)

                # user.password = _one_portal_crypted_password
                # print(_one_portal_crypted_password)

                user.profile_picture = portal_data['profile_picture']

                self.orm_session.add(user)
                added += 1
        self.orm_session.commit()
        return {'added': added}


@base.route(URI="/portal-login")
class PortalUserLoginHandler(base.Base):

    @base.api()
    async def post(self, username, password):
        http_client = AsyncHTTPClient()
        target = os.getenv('ONEPORTAL', 'telmekom-one.dev.digitalcube.rs')
        uri = f'https://{target}/user/login'
        try:
            response = await http_client.fetch(uri, method='POST',
                                               body=json.dumps({'username': username, 'password': password}))
            result = json.loads(response.body)
            if 'token' in result:
                return check_portal_user(result['token'], self)
            raise http.HttpInternalServerError({'message': 'Token not found'})

        except Exception as e:
            raise http.HttpErrorUnauthorized({'message': f'Error logging user on portal {target}', 'e': str(e)})

        pass


def check_portal_user(portal_token, handler):
    with one_portal_orm.telmekom_orm_session() as session:

        id_one_user = None
        for l in session.execute("select id_user from session_tokens where active=1 and id=:portal_token",
                                 {'portal_token': portal_token}):
            id_one_user = l[0]
            break

        if not id_one_user:
            raise http.HttpErrorUnauthorized

        try:
            au = session.execute("select username, role_flags, password from auth_users where id=:uid",
                                 {'uid': id_one_user}).next()

            _email = au[0]
            _one_portal_roleflags = au[1]

            _one_portal_crypted_password = au[2]

            u = session.execute(
                "select client_name, first_name, last_name, profile_picture, org_unit from users where id=:uid",
                {'uid': id_one_user}).next()

            _client_name = u[0]
            _first_name = u[1]
            _last_name = u[2]
            _profile_picture = u[3]
            _org_unit = u[4]

            portal_data = {'id': id_one_user,
                           'email': _email,
                           'roleflags': _one_portal_roleflags,
                           'client_name': _client_name,
                           'first_name': _first_name,
                           'last_name': _last_name,
                           'profile_picture': _profile_picture,
                           'org_unit': _org_unit
                           }
        except:
            raise http.HttpErrorUnauthorized

    user = handler.orm_session.query(models.User).filter(models.User.username == portal_data['email']).one_or_none()

    # TODO: Transformacija roleflags, odnosno implementacija neophodnih
    role_flags = 1

    if not user:
        user = models.User(username=portal_data['email'],
                           password='123',
                           role_flags=role_flags,
                           first_name=portal_data['first_name'],
                           last_name=portal_data['last_name'],
                           email=portal_data['email'],
                           org_unit=portal_data['org_unit'])

        # user.password = _one_portal_crypted_password
        # print(_one_portal_crypted_password)

        user.profile_picture = portal_data['profile_picture']

        handler.orm_session.add(user)

    return create_new_user_session(handler.orm_session, portal_data['email'], '123')


@base.route(URI="/portal")
class PortalUserHandler(base.Base):

    @base.api()
    async def post(self, portal_token):
        return check_portal_user(portal_token, self)


@base.route(URI="/check-token")
class CheckToken(base.Base):

    @base.auth()
    @base.api()
    async def get(self):
        return None


def create_new_user_session(orm_session, username, password):
    user = orm_session.query(models.User).filter(models.User.username == username,
                                                 models.User.password == password).one_or_none()
    if not user:
        raise http.HttpErrorUnauthorized

    token = models.Session(user)
    orm_session.add(token)
    orm_session.commit()

    import base
    base.store.set(token.id, '1')

    return {'id': user.id, 'token': token.jwt}, http.status.CREATED
