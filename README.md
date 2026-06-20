# GoatCalendar

- [GoatCalendar](#goatcalendar)
- [Installation en dev](#installation-en-dev)
  - [Back](#back)
  - [Front](#front)
- [Installation en prod](#installation-en-prod)

# Installation en dev

You must have **Python 3.13** or higher installed, to build and start back-end and front-end service.

## Back

To create mysql container for project:

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

To execute tests :
```bash
pdm run pytest
```

To run services : 
```bash
pdm run dev_win
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
FRONT_URL="http://localhost:8080"
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
FRONT_URL="http://localhost:8080"
ENCRYPTION_KEY="q+b4dGwz4nZOjdoYvOwurO781EPliCKWxo0/2bTb7NeBN/lsybkh0EU+mWiefEtFtcIOrv0yZJHuakJQGYQz1Q=="
ACCESS_TOKEN_DURATION_MINUTES=1000
REFRESH_TOKEN_DURATION_HOURS=24
```

## Front

Le front est volontairement statique : HTML, CSS et JavaScript natif uniquement.

Configuration API par défaut :

- Auth service : `http://localhost:5001`
- Board service : `http://localhost:5002`

Pour lancer le front en dev :

```bash
cd front
py -m http.server 8080
```

Puis ouvrir `http://localhost:8080`.

Les URLs des services sont centralisées dans `front/scripts/config.js`.

Comptes de demo seedés :

- `aliceproprio@gmail.com`
- `boblocataire@gmail.com`
- `clairemixte@gmail.com`

Mot de passe : `azerty`

# Installation en prod

Pour lancer les services, se positionner dans le répertoire **GoatCalendar** :
```bash
docker-compose pull
docker-compose build
docker-compose up
```

Puis ouvrir `http://localhost:8080`.

Comptes de demo seedés :

- `aliceproprio@gmail.com`
- `boblocataire@gmail.com`
- `clairemixte@gmail.com`

Mot de passe : `azerty`