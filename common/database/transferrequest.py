from sqlalchemy import Column, String, Integer, DateTime

from common.database.base import base


class TransferRequest(base):
    __tablename__ = 'transferrequest'
    __table_args__ = {'extend_existing': True}
    transfer_request_key = Column(Integer, primary_key=True)
    doctor_id = Column(Integer)
    target_hospital_id = Column(Integer)
    patient_id = Column(Integer)
    created_datetime = Column(DateTime)
    status = Column(String)
