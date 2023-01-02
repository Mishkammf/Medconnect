from sqlalchemy import Column, String, Integer, DateTime, ForeignKey

from common.database.base import base


class UserToken(base):
    __tablename__ = 'user_tokens'

    id = Column(Integer, primary_key=True)
    user_key = Column(Integer, ForeignKey('tenant_users.user_key'))
    token = Column(String)
    token_expiry = Column(DateTime)
    created_datetime = Column(DateTime)
    modified_datetime = Column(DateTime)
