

from sqlalchemy import Column, String, Integer, DateTime, Boolean

from common.database.base import base


class Admin(base):
    __tablename__ = 'admin'
    admin_key = Column(Integer, primary_key=True)
    password = Column(String)
    login_id = Column(String)
    admin_group_key = Column(Integer)
    token = Column(String)
    token_expiry = Column (String)
    created_datetime = Column(DateTime)
    modified_datetime = Column(DateTime)
    mobile_number = Column(String)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=1)
    created_user = Column(Integer)
    modified_user = Column(Integer)



