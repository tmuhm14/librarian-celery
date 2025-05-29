from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class RunLogs(Base):
    __tablename__ = 'run_logs'

    id = Column(Integer, autoincrement=True, primary_key=True)
    run_id = Column(String, nullable=False)
    run_mode = Column(String, nullable=True)
    run_start_time = Column(DateTime, nullable=True)
    run_end_time = Column(DateTime, nullable=True)
    run_status = Column(String, nullable=True)


class RequestLogs(Base):
    __tablename__ = 'request_logs'

    id = Column(Integer, autoincrement=True, primary_key=True)
    request_id = Column(String, nullable=False)
    request_time = Column(DateTime, nullable=True)
    request_status = Column(String, nullable=True)
    request_type = Column(String, nullable=True)
    request_url = Column(String, nullable=True)
    request_data = Column(JSON, nullable=True)
    response_time = Column(DateTime, nullable=True)
    response_status = Column(String, nullable=True)
    response_data = Column(JSON, nullable=True)


class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=True)
    pd_ref = Column(String, nullable=True)
    pb_ref = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=True)


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, autoincrement=True, primary_key=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    pd_ref = Column(String, nullable=True)
    pb_ref = Column(String, nullable=True)
    source_detail = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=True)
    pd_org_id = Column(String, nullable=True)


class ContactSyncLog(Base):
    __tablename__ = 'contact_sync_log'

    id = Column(Integer, autoincrement=True, primary_key=True)
    contact_id = Column(Integer, nullable=True)
    phoneburner_id = Column(String, nullable=True)
    pipedrive_id = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    folder_id = Column(String, nullable=True)
    folder_name = Column(String, nullable=True)
    sync_type = Column(String, nullable=True)
    import_result = Column(String, nullable=True)
    sync_status = Column(String, nullable=True)
    sync_time = Column(DateTime, nullable=True)


class Campaign(Base):
    __tablename__ = 'campaigns'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=True)
    pd_value = Column(Integer, nullable=True)


class Score(Base):
    __tablename__ = 'scores'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=True)
    pd_value = Column(Integer, nullable=True)
