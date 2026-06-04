# GoatCalendar

- [GoatCalendar](#goatcalendar)
- [Installation en dev](#installation-en-dev)
  - [Back](#back)
  - [Front](#front)
  - [Installation en prod](#installation-en-prod)
  - [Back](#back-1)
  - [Front](#front-1)

# Installation en dev

https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/ci-based-analysis/gitlab-ci

## Back

To create mysql container for project:

```bash
docker run -d -e MYSQL_ROOT_PASSWORD=azerty -e MYSQL_DATABASE=goatcalendar_db -e MYSQL_USER=goatcalendar_user -e MYSQL_PASSWORD=goatcalendar_passwd -p 3306:3306 mysql:latest
```

To setup PyPI credentials for the current project :

```bash
pdm config --local repository.pypi.username __token__
pdm config --local repository.pypi.password pypi-YOUR_SECRET_TOKEN_HERE
```

It will create at the root of the project, a file named `pdm.toml` with following content :
```bash
[repository.pypi]
username = "__token__"
password = "pypi-YOUR_SECRET_TOKEN_HERE"
```

To publish new version for the project in PyPI :
```bash
pdm publish
```

To install dev dependancies for the project :

```bash
pdm lock --dev -G:all
pdm install --group test --group dev
```

To update local dependancies :
```bash
pdm install --dev -G:all
```

To export dependancies for production (used automatically in dockerfile) :
```bash
pdm export --pyproject --prod --group prod --format requirements --output requirements.txt --no-hashes
```

Create a `.env` file for each project in `back` folder :

- Database service

```bash
ENV_MODE="prod"
DB_DIALECT="mysql+aiomysql"
DB_URL="goatcalendar_user:goatcalendar_passwd@localhost:3306/goatcalendar_db"
```

- Auth service

```bash
ENV_MODE="prod"

DB_DIALECT="mysql+aiomysql"
DB_URL="goatcalendar_user:goatcalendar_passwd@localhost:3306/goatcalendar_db"
SERVER_HOST="127.0.0.1"
SERVER_PORT=5001
FRONT_URL="127.0.0.1:80"
ENCRYPTION_KEY="q+b4dGwz4nZOjdoYvOwurO781EPliCKWxo0/2bTb7NeBN/lsybkh0EU+mWiefEtFtcIOrv0yZJHuakJQGYQz1Q=="
ACCESS_TOKEN_DURATION_MINUTES=1000
REFRESH_TOKEN_DURATION_HOURS=24
```

- Board service

```bash
ENV_MODE="prod"
DB_DIALECT="mysql+aiomysql"
DB_URL="goatcalendar_user:goatcalendar_passwd@localhost:3306/goatcalendar_db"
SERVER_HOST="127.0.0.1"
SERVER_PORT=5002
FRONT_URL="127.0.0.1:80"
ENCRYPTION_KEY="q+b4dGwz4nZOjdoYvOwurO781EPliCKWxo0/2bTb7NeBN/lsybkh0EU+mWiefEtFtcIOrv0yZJHuakJQGYQz1Q=="
ACCESS_TOKEN_DURATION_MINUTES=1000
REFRESH_TOKEN_DURATION_HOURS=24
```

## Front



## Installation en prod

## Back

-  Database service

```bash
ENV_MODE="prod"
DB_DIALECT="mysql+aiomysql"
DB_URL="goatcalendar_user:goatcalendar_passwd@mysql-db:3306/goatcalendar_db"
```

- Auth service

```bash
ENV_MODE="prod"
DB_DIALECT="mysql+aiomysql"
DB_URL="goatcalendar_user:goatcalendar_passwd@mysql-db:3306/goatcalendar_db"
SERVER_HOST="0.0.0.0"
SERVER_PORT=5001
FRONT_URL="front-service:80"
ENCRYPTION_KEY="q+b4dGwz4nZOjdoYvOwurO781EPliCKWxo0/2bTb7NeBN/lsybkh0EU+mWiefEtFtcIOrv0yZJHuakJQGYQz1Q=="
ACCESS_TOKEN_DURATION_MINUTES=1000
REFRESH_TOKEN_DURATION_HOURS=24
```

- Board service

```bash
ENV_MODE="prod"
DB_DIALECT="mysql+aiomysql"
DB_URL="goatcalendar_user:goatcalendar_passwd@mysql-db:3306/goatcalendar_db"
SERVER_HOST="0.0.0.0"
SERVER_PORT=5002
FRONT_URL="front-service:80"
ENCRYPTION_KEY="q+b4dGwz4nZOjdoYvOwurO781EPliCKWxo0/2bTb7NeBN/lsybkh0EU+mWiefEtFtcIOrv0yZJHuakJQGYQz1Q=="
ACCESS_TOKEN_DURATION_MINUTES=1000
REFRESH_TOKEN_DURATION_HOURS=24
```

## Front