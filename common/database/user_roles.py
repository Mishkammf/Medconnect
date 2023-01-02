

from sqlalchemy import Column, String, Integer, DateTime

from common.database.base import base


class UserRole(base):
    __tablename__ = 'user_roles'
    user_role_key = Column(Integer, primary_key=True)
    user_role = Column(String)
    role_type = Column(String)
    created_datetime = Column(DateTime)
    modified_datetime = Column(DateTime)
    role_group_key = Column(Integer)
    role_description = Column(String)
