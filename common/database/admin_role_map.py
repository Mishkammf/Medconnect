
import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey

from common.database.base import base


class AdminRolesAdminGroupMap(base):
    __tablename__ = 'admin_role_admin_group_map'
    map_key = Column(Integer, primary_key=True)
    admin_group_key = Column(Integer, ForeignKey('admin_groups.admin_group_key'))
    admin_role_key = Column(Integer, ForeignKey('admin_roles.admin_role_key'))
    created_datetime = Column(DateTime, default=datetime.datetime.utcnow())
    modified_datetime = Column(DateTime, default=datetime.datetime.utcnow())

    def __init__(self, admin_group_key=None, admin_role_key=None):
        self.admin_group_key = admin_group_key
        self.admin_role_key = admin_role_key
