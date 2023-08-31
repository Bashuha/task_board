from config import MYSQL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(
    f'mysql+mysqlconnector://{MYSQL.get("user")}:{MYSQL.get("password")}@localhost/{MYSQL.get("database")}?auth_plugin=mysql_native_password',
    echo=MYSQL.getboolean('echo'),
    pool_pre_ping=True,
    connect_args={'charset':'utf8'}
)
Session = sessionmaker(bind=engine)