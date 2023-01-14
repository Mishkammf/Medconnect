

from sqlalchemy import Column, String, Integer, DateTime

from common.database.base import base


class User(base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    user_key = Column(Integer, primary_key=True)
    user_password = Column(String)
    user_login_id = Column(String)
    created_datetime = Column(DateTime)
    modified_datetime = Column(DateTime)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)





