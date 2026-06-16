import os

os.environ.setdefault("ENV_MODE", "dev")
os.environ.setdefault("DB_DIALECT", "mysql+aiomysql")
os.environ.setdefault("DB_URL", "user:password@localhost:3306/test")
