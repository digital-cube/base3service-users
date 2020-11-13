import base
import sqlalchemy.exc as sqaexc
from base import paginate, http
import bcrypt

import orm.models as models

import datetime

import lookup.user_permissions as perm


import sqlalchemy

if base.config.conf['apptype'] == 'monolith':
    base.route.set('prefix', base.config.conf['services']['users']['prefix'])
else:
    base.route.set('prefix', base.config.conf['prefix'])


@base.route('/about')
class AboutUserServiceHandler(base.Base):

    @base.api()
    async def get(self):
        return {'service': 'users'}


def format_password(user, password):
    return f"{user.id}{password}"


def encrypt_password(user):
    return bcrypt.hashpw(format_password(user, user.password).encode(), bcrypt.gensalt()).decode('ascii')


def check_password(user, password):
    return bcrypt.checkpw(format_password(user, password).encode(), user.password.encode())


def allow_password(user, password):
    if len(password) < 6:
        raise base.http.HttpInvalidParam(
            id_message='PASSWORD_FORMAT',
            message="Password should contains minimum 6 characters",
        )

    return True


def change_user_data(user: models.User, data: dict, change_by: models.User = None):
    orm_session = sqlalchemy.inspect(user).session

    if not change_by:
        change_by = user

    password_changed = False

    def can_change_password():
        # if user tries to change his own password, user need to provide old password
        if 'password' in data:
            if 'old_password' not in data:
                raise http.HttpErrorUnauthorized(id_message='MISSING_PARAM_OLD_PASSWORD',
                                                 message='Old password is mandatory parameter for changig password')

            if not check_password(user, data['old_password']):
                raise http.HttpErrorUnauthorized

            del data['old_password']

            return True

        return None

    def user_change_his_own_password():
        if can_change_password():
            plain_password = data['password']

            if allow_password(user, plain_password):
                user.password = plain_password
                user.password = encrypt_password(user)
                del data['password']

                return True

        return False

    can_change = ['email', 'first_name', 'last_name', 'password']

    # if user is not admin, user can change properties only for himself
    if change_by.permission_flags & perm.ADMIN == 0:
        if change_by.id != user.id:
            raise http.HttpErrorUnauthorized

        if user_change_his_own_password():
            password_changed = True

    else:
        # if user is admin, then admin can change permission flag to
        can_change += ['permission_flags']

        if 'password' in data:
            # if admin tries to change his own password, admin need to provide old password as well
            if change_by.id == user.id:
                if user_change_his_own_password():
                    password_changed = True

            else:
                # admin can change users password without old password
                # admin can set any password to target user, avoiding allow_password()

                plain_password = data['password']
                user.password = plain_password
                user.password = encrypt_password(user)
                del data['password']
                password_changed = True

    # restricting parameters to can_change
    data = {p: data[p] for p in data if p in can_change}

    updated = user.update(data)
    if password_changed:
        updated += ['password']

    if updated:
        try:
            orm_session.commit()
        except:
            orm_session.rollback()
            raise http.HttpInternalServerError(id_message='DATABASE_UPDATE_ERROR',
                                               message='Problem updateing user')

    return updated


@base.route('/admin')
class AdminHandler(base.Base):

    @base.auth(permissions=perm.ADMIN)
    @base.api()
    async def get(self, page: int = 1, per_page: int = 10, permission_flags: int = None,
                  fields='id,username,email,first_name,last_name'):
        fields = fields.replace(' ', '').split(',') if fields else []

        filters = [models.User.active == True]
        if permission_flags is not None:
            filters.append(models.User.permission_flags.op('&')(permission_flags) != 0)

        query, summary = paginate(self.orm_session.query(models.User).filter(*filters),
                                  base.route.get('prefix') + '/', page, per_page)

        return {'summary': summary,
                'users': [user.serialize(fields) for user in query]}

        pass


@base.route('/admin/:id_user')
class AdminSingleUsersHandler(base.Base):

    @base.auth(permissions=perm.ADMIN)
    @base.api()
    async def get(self, user: models.User.id, fields='id,username,email,first_name,last_name'):
        if not user:
            raise http.HttpErrorNotFound

        fields = fields.replace(' ', '').split(',') if fields else []

        return user.serialize(fields)

    @base.auth(permissions=perm.ADMIN)
    @base.api()
    async def patch(self, user: models.User.id, data: dict):

        if not user:
            raise http.HttpErrorNotFound

        logged_user = self.orm_session.query(models.User).filter(models.User.id == self.id_user).one_or_none()
        return change_user_data(user, data, change_by=logged_user)

    @base.auth(permissions=perm.ADMIN)
    @base.api()
    async def delete(self, user: models.User.id):

        if not user:
            raise http.HttpErrorNotFound

        user.username = f'removed;{user.id};{user.username}'
        user.active = False
        self.orm_session.commit()


@base.route('/')
class UsersHandler(base.Base):

    @base.api()
    async def post(self, user: models.User):

        if user.permission_flags and user.permission_flags & perm.ADMIN != 0:
            # admin user can only be regitered if there is no user registered in the database
            if self.orm_session.query(models.User).count():
                raise http.HttpErrorUnauthorized(
                    message="admin user can only be regitered if there is no user registered",
                    id_message="NOT_ALLOWED_TO_REGISTER_ADMIN_USER")

        allow_password(user, user.password)

        user.password = encrypt_password(user)
        self.orm_session.add(user)

        try:
            self.orm_session.commit()
        except sqaexc.IntegrityError as e:
            raise base.http.HttpInternalServerError("User already exists",
                                                    'USER_ALREADY_EXISTS')
        except Exception as e:
            raise base.http.HttpInternalServerError

        return {'id': user.id}, http.status.CREATED

    @base.auth()
    @base.api()
    async def get(self):
        logged_user = self.orm_session.query(models.User).filter(models.User.id == self.id_user).one_or_none()
        return logged_user.serialize()

    @base.auth()
    @base.api()
    async def patch(self, data: dict):
        logged_user = self.orm_session.query(models.User).filter(models.User.id == self.id_user).one_or_none()
        return change_user_data(logged_user, data)


@base.route('/sessions')
class SessionsHandler(base.Base):
    @base.api()
    async def post(self, username: str, password: str):
        user = self.orm_session.query(models.User). \
            filter(models.User.username == username,
                   models.User.active == True).one_or_none()

        if not user:
            raise base.http.HttpErrorUnauthorized

        if not check_password(user, password):
            raise base.http.HttpErrorUnauthorized

        session = models.Session(user)
        self.orm_session.add(session)
        self.orm_session.commit()

        base.store.set(session.id, 1)

        return {'id': session.id,
                'token': session.jwt}, http.status.CREATED

    @base.auth()
    @base.api()
    async def delete(self):

        base.store.set(self.id_session, 0)

        session = self.orm_session.query(models.Session).filter(models.Session.id == self.id_session).one_or_none()
        if session:
            session.active = False
            session.closed = datetime.datetime.now()
            try:
                self.orm_sessiom.commit()
            except:
                pass

        return None


@base.route('/forgot')
class ForgotPasswordHandler(base.Base):
    @base.api()
    async def post(self, username: str):
        user = self.orm_session.query(models.User).filter(
            models.User.username == username.lower().strip()).one_or_none()

        # if there is no user found, OK - 201 NO Content is response, because of potential hacking
        if not user:
            return None

        reset_passwod = models.ForgotPasswordId(user=user)
        self.orm_session.add(reset_passwod)

        try:
            self.orm_session.commit()
        except:
            self.orm_session.rollback()
            raise http.HttpInternalServerError

        # TODO: Send email via mail queue service and return None

        base.store.set('tmp_test_last_reset_password_id', reset_passwod.id)

        return None
        # return {'id': reset_passwod.id}


@base.route('/reset/:id_forgot')
class ResetPasswordHandler(base.Base):

    @base.api()
    async def post(self, forgot: models.ForgotPasswordId.id, password: str):

        if not forgot:
            return None

        if forgot.expired:
            raise http.HttpErrorUnauthorized(id_message='FORGOT_PASSWORD_CODE_EXPIRED_OR_USED',
                                             message='Forgot password code has expired, or already used')

        user = forgot.user
        allow_password(user, password)

        user.password = password
        user.password = encrypt_password(user)
        forgot.expired = datetime.datetime.now()

        try:
            self.orm_session.commit()
        except:
            self.orm_session.rollback()
            raise http.HttpInternalServerError

        return None
