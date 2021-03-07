#!/bin/sh

cd /app && aerich upgrade && python scripts/tmp/seed_users_from_openlight.py && python users.py
#cd /app && aerich upgrade && sleep 1 && python scripts/tmp/seed_users_from_openlight.py && python users.py
