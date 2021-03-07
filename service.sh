#!/bin/sh

cd /app && python wait4db.py && aerich upgrade &&  python service.py

#cd /app && python wait4db.py && aerich upgrade && sleep 1 && python scripts/tmp/seed_users.py && python service.py