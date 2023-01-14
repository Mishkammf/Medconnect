from sqlalchemy import Column, String, Integer, DateTime

from common.database.base import base


class AmbulanceRequest(base):
    __tablename__ = 'ambulancerequest'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    ambulance_id = Column(Integer)
    doctor_id = Column(Integer)
    start_hospital_id = Column(Integer)
    end_hospital_id = Column(Integer)
    created_datetime = Column(DateTime)
    status = Column(String)
