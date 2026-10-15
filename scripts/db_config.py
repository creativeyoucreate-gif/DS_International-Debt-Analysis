import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL

DB_USER     = "postgres"
DB_PASSWORD = os.environ.get("DB_PASSWORD", "KAvi")   # better: set DB_PASSWORD as an environment variable
DB_HOST     = "localhost"
DB_PORT     = 5432
DB_NAME     = "intl_debt"

engine = create_engine(URL.create("postgresql+psycopg2", username=DB_USER,
                                  password=DB_PASSWORD, host=DB_HOST,
                                  port=DB_PORT, database=DB_NAME))