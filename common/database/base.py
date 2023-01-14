

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from common.config_manager import get_config

config = get_config('database')

# create an engine
mysql_connection = 'mysql://' + config['user'] + ':mishka123@' + config['host'] + '/' + config[
   'db']
engine = create_engine(mysql_connection, connect_args={'connect_timeout': 20}, pool_pre_ping=True, convert_unicode=True,
                       echo=False, echo_pool=True,
                       pool_size=0,
                       max_overflow=10,
                       pool_recycle=3600)

# create a configured "Session" class
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

base = declarative_base()
