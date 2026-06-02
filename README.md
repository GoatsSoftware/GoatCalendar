# GoatCalendar

- [GoatCalendar](#goatcalendar)
- [Installation en dev](#installation-en-dev)
  - [Back](#back)
    - [Publish des services sur Pypi](#publish-des-services-sur-pypi)
    - [Database service](#database-service)
    - [Auth service](#auth-service)
    - [Board service](#board-service)
  - [Front](#front)
  - [Installation en prod](#installation-en-prod)
  - [Back](#back-1)
    - [Database service](#database-service-1)
    - [Auth service](#auth-service-1)
    - [Board service](#board-service-1)
  - [Front](#front-1)

# Installation en dev

## Back

```bash
docker run -d -e MYSQL_ROOT_PASSWORD=azerty -e MYSQL_DATABASE=goatcalendar_db -e MYSQL_USER=goatcalendar_user -e MYSQL_PASSWORD=goatcalendar_passwd -p 3306:3306 mysql:latest
```

### Publish des services sur Pypi

```bash
pdm config --local repository.pypi.username __token__
pdm config --local repository.pypi.password pypi-YOUR_SECRET_TOKEN_HERE
pdm publish
```

Dependancies installation

```bash
pdm install --group test --group dev
```

Export des lib :
```bash
pdm export --pyproject --prod --group prod --format requirements --output requirements.txt --no-hashes
```

### Database service

```bash
ENV_MODE="prod"
DB_DIALECT="mysql+aiomysql"
DB_URL="goatcalendar_user:goatcalendar_passwd@localhost:3306/goatcalendar_db"
```

### Auth service

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

### Board service

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

### Database service

```bash
ENV_MODE="prod"
DB_DIALECT="mysql+aiomysql"
DB_URL="goatcalendar_user:goatcalendar_passwd@mysql-db:3306/goatcalendar_db"
```

### Auth service

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

### Board service

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