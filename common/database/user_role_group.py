
from sqlalchemy import Column, String, Integer, DateTime

from common.database.base import base


class UserRoleGroup(base):
    __tablename__ = 'user_role_group'

    role_group_key = Column(Integer, primary_key=True)
    role_group = Column(String)
    created_datetime = Column(DateTime)
    modified_datetime = Column(DateTime)
