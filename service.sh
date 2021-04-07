#!/usr/bin/env bash

if [[ $APP_ENVIRONMENT == "prod" ]]
then
  cd /app && aerich upgrade &&  python service.py
else
  cd /app && python wait4db.py && aerich upgrade &&  python service.py
fi
