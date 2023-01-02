

from sqlalchemy import Column, String, Integer, DateTime

from common.database.base import base


class AdminRole(base):
    __tablename__ = 'admin_roles'
    admin_role_key = Column(Integer, primary_key=True)
    admin_role = Column(String)
    role_type = Column(String)
    role_group_key = Column(Integer)
    created_datetime = Column(DateTime)
    modified_datetime = Column(DateTime)
    role_group_key = Column(Integer)
    role_description = Column(String)
