
test:
	coverage --version
	pytest --version
	coverage run -m pytest --disable-warnings --maxfail=1 --doctest-modules --ignore=statsd/defaults/django.py .
	coverage run -m pytest --disable-warnings --ignore=statsd/defaults/django.py statsd/tests.py
	coverage report -m

lint:
	ruff --version
	ruff check --target-version=py37 --respect-gitignore --select I --line-length=120 .
	mypy --version
	mypy --python-version=3.8 --ignore-missing-imports .

lint-fix:
	ruff --version
	ruff check --target-version=py37 --respect-gitignore --select I --fix --line-length=120 .
	ruff format --target-version=py37 --respect-gitignore --exit-non-zero-on-format --line-length=120 .
