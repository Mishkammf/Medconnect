

from sqlalchemy import Column, String, Integer, DateTime

from common.database.base import base


class AdminLoginHistory(base):
    __tablename__ = 'admin_login_history'

    admin_key = Column(Integer, primary_key=True, )
    ip_address = Column(String)
    logged_in_out_datetime = Column(DateTime)
    is_login = Column(Integer)
    device = Column(Integer, default=0)
    created_datetime = Column(DateTime)
    modified_datetime = Column(DateTime)
