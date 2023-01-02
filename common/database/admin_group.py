

from sqlalchemy import Column, String, Integer, DateTime

from common.database.base import base


class AdminGroup(base):
    __tablename__ = 'admin_groups'
    admin_group_key = Column(Integer, primary_key=True)
    admin_group = Column(String)
    created_datetime = Column(DateTime)
    modified_datetime = Column(DateTime)
    created_user = Column(Integer)
    modified_user = Column(Integer)
