from sqlalchemy.engine import create_engine
import os
import sys
from sqlalchemy.exc import OperationalError

# GET ALL NEEDED KARMA ENV VARIABLE
EnvLoader.load_env()

mysql_url = os.getenv('MYSQL_URL')
mysql_user = os.getenv('MYSQL_USER')
mysql_port = os.getenv('MYSQL_PORT')
mysql_database = os.getenv('MYSQL_DATABASE')

def get_engine():
    try:
        mysql_password_root = os.environ.get('MYSQL_ROOT_PASSWORD')
    except:
        print("Root MySql Password is not in MYSQL_ROOT_PASSWORD Env variable") 
        sys.exit(1)


    # recreating the URL connection
    connection_url = 'mysql://{user}:{password}@{url}:{mysql_port}/{mysql_database}'.format(
        user=mysql_user,
        password=mysql_password_root,
        url=mysql_url,
        mysql_port=mysql_port,
        mysql_database=mysql_database
    )

    return create_engine(connection_url)

def test_database_connection():
    """
    Check if karma mysql connection is available, return True or False

    Parameters
    ----------

    Example
    -------
    test_database_connection()
    """
    try:
        engine = get_engine()
        with engine.connect() as connection:
            pass
            # connection is closed in with context
        return True
    except OperationalError:
        return False