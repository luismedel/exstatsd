
test:
	coverage run -m pytest --disable-warnings --maxfail=1 --doctest-modules --ignore=statsd/defaults/django.py .
	coverage run -m pytest --disable-warnings --ignore=statsd/defaults/django.py statsd/tests.py
	coverage report -m

lint:
	ruff check --target-version=py37 --respect-gitignore --select I .
	mypy --python-version=3.8 --ignore-missing-imports --line-length=120 .

lint-fix:
	ruff check --target-version=py37 --respect-gitignore --select I --fix .
	ruff format --target-version=py37 --respect-gitignore --exit-non-zero-on-format .
