echo "testing users service; test log file is /tmp/test_users.log" && .venv/bin/python3 -m unittest tests/test_*.py 1>/tmp/test_users.log
