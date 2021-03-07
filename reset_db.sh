if [[ $1 == "full" ]]
then
  sudo rm -rf aerich.ini migrations
  aerich init -t config.config.TORTOISE_ORM
  aerich --app=users init-db
else
  aerich upgrade
fi

#python setup_db.py