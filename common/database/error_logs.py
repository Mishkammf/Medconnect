

from sqlalchemy import Column, String, Integer, DateTime

from common.database.base import base


class ErrorLog(base):
    __tablename__ = 'error_log'

    error_key = Column(Integer, primary_key=True)
    error_message = Column(String)
    error_type = Column(String)
    tenant_key = Column(Integer)
    created_datetime = Column(DateTime)
    modified_datetime = Column(DateTime)
