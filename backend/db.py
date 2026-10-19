import os

import psycopg2


def get_conn():
    """Abre una conexión PostgreSQL usando las variables DB_* del archivo .env."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "roadmap_db"),
        user=os.getenv("DB_USER", "roadmap_user"),
        password=os.getenv("DB_PASSWORD", ""),
    )
