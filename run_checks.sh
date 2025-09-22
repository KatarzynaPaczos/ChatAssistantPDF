# run_checks.sh
vulture app/
vulture main.py
ruff check app/
ruff check . --fix
ruff check .