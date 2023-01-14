from sqlalchemy import Column, Integer, String
from common.database.base import base
class Hospital(base):
    __tablename__ = 'hospital'
    __table_args__ = {'extend_existing': True}
    hospital_key = Column(Integer, primary_key=True)
    name = Column(String)
    total_gicu_beds_available = Column(Integer)
    total_gicu_beds_used = Column(Integer)
    total_sicu_beds_available = Column(Integer)
    total_sicu_beds_used = Column(Integer)
