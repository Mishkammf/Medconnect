
import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey

from common.database.base import base


class UserRolesUserGroupMap(base):
    __tablename__ = 'user_role_user_group_map'
    map_key = Column(Integer, primary_key=True)
    user_group_key = Column(Integer, ForeignKey('user_groups.user_group_key'))
    user_role_key = Column(Integer, ForeignKey('user_roles.user_role_key'))
    created_datetime = Column(DateTime, default=datetime.datetime.utcnow())
    modified_datetime = Column(DateTime, default=datetime.datetime.utcnow())

    def __init__(self, user_group_key=None, user_role_key=None):
        self.user_group_key = user_group_key
        self.user_role_key = user_role_key
