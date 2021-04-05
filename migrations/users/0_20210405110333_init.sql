-- upgrade --
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "tenants" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(64) NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS "idx_tenants_name_2ea023" ON "tenants" ("name");
CREATE TABLE IF NOT EXISTS "auth_users" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "username" VARCHAR(64) NOT NULL UNIQUE,
    "password" VARCHAR(64) NOT NULL,
    "role_flags" INT NOT NULL  DEFAULT 1,
    "active" BOOL NOT NULL  DEFAULT True,
    "scopes" JSONB,
    "id_tenant" UUID REFERENCES "tenants" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_auth_users_usernam_2be66c" ON "auth_users" ("username");
CREATE INDEX IF NOT EXISTS "idx_auth_users_role_fl_f9e3ab" ON "auth_users" ("role_flags");
CREATE INDEX IF NOT EXISTS "idx_auth_users_active_f63f0d" ON "auth_users" ("active");
CREATE INDEX IF NOT EXISTS "idx_auth_users_id_tena_d3cc9a" ON "auth_users" ("id_tenant");
CREATE TABLE IF NOT EXISTS "sessions" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "closed" TIMESTAMPTZ,
    "active" BOOL NOT NULL  DEFAULT True,
    "ttl" INT,
    "id_user" UUID NOT NULL REFERENCES "auth_users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_sessions_active_8396b5" ON "sessions" ("active");
CREATE INDEX IF NOT EXISTS "idx_sessions_id_user_b48b8c" ON "sessions" ("id_user");
CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "first_name" VARCHAR(64),
    "last_name" VARCHAR(64),
    "email" VARCHAR(64),
    "alarm_type" INT NOT NULL  DEFAULT 0,
    "notification_type" INT NOT NULL  DEFAULT 0,
    "phone" VARCHAR(64),
    "data" JSONB,
    "language" VARCHAR(16) NOT NULL  DEFAULT 'en',
    "id_auth_user" UUID NOT NULL UNIQUE REFERENCES "auth_users" ("id") ON DELETE CASCADE
);
