
from datetime import datetime
from data.db import db_connect, create_session
from dotenv import load_dotenv
from sqlalchemy import text
from models import RunLogs, RequestLogs, Organization, Contact, ContactSyncLog
load_dotenv()

engine, connection = db_connect()
session = create_session(engine)


def create_run_log(run_id, run_mode, run_status="started"):
    run_log = RunLogs(run_id=run_id, run_mode=run_mode,
                      run_start_time=datetime.now(), run_status=run_status)
    session.add(run_log)
    session.commit()


def update_run_log(run_id, run_status="completed"):
    run_log = session.query(RunLogs).filter(RunLogs.run_id == run_id).first()
    run_log.run_end_time = datetime.now()
    run_log.run_status = run_status
    session.commit()


def get_latest_run_log():
    run_log = session.query(RunLogs).order_by(
        RunLogs.run_start_time.desc()).first()
    return run_log


def create_request_log(request_id, request_type, request_data, request_status="success", request_time=None):
    request_log = RequestLogs(request_id=request_id, request_type=request_type,
                              request_data=request_data, request_status=request_status, request_time=request_time)
    session.add(request_log)
    session.commit()


def update_request_log(request_id,  response_time=None, response_status=None, response_data=None):
    request_log = session.query(RequestLogs).filter(
        RequestLogs.request_id == request_id).first()
    print(request_log)
    request_log.response_time = response_time
    request_log.response_status = response_status
    request_log.response_data = response_data
    session.commit()


def get_organization_by_name(name):
    organization = session.query(Organization).filter(
        Organization.name == name).first()
    return organization


def get_organization_by_pb_ref(pb_ref):
    organization = session.query(Organization).filter(
        Organization.pb_ref == str(pb_ref)).first()
    return organization


def get_organization_by_pd_ref(pd_ref):
    organization = session.query(Organization).filter(
        Organization.pd_ref == str(pd_ref)).first()
    return organization


def upsert_organization(organization):
    existing_organization = session.query(Organization).filter(
        Organization.pd_ref == str(organization.pd_ref)).first()
    if existing_organization:
        existing_organization.pb_ref = organization.pb_ref
        existing_organization.is_active = organization.is_active
        existing_organization.updated_at = datetime.now()
        existing_organization.updated_by = "sync"
    else:
        organization.created_at = datetime.now()
        organization.created_by = "sync"
        organization.updated_at = datetime.now()
        organization.updated_by = "sync"
        session.add(organization)
    session.commit()


def upsert_contact(contact):
    existing_contact = session.query(Contact).filter(
        Contact.pd_ref == str(contact.pd_ref)).first()
    if existing_contact:
        print(
            f"[DEBUG] Updating {existing_contact.first_name} {existing_contact.last_name}")
        existing_contact.first_name = contact.first_name
        existing_contact.last_name = contact.last_name
        existing_contact.pd_org_id = contact.pd_org_id
        existing_contact.source_detail = contact.source_detail
        existing_contact.updated_at = datetime.now()
        existing_contact.updated_by = "sync"

    else:
        print(f"[DEBUG] Creating {contact.first_name} {contact.last_name}")
        contact.created_at = datetime.now()
        contact.created_by = "sync"
        contact.updated_at = datetime.now()
        contact.updated_by = "sync"
        session.add(contact)
    session.commit()


def get_all_contacts():
    contacts = session.query(Contact).all()
    return contacts


def get_contact_by_pd_ref(pd_ref):
    contact = session.query(Contact).filter(
        Contact.pd_ref == str(pd_ref)).first()
    return contact


def add_contact_sync_log(contact_sync_log):
    session.add(contact_sync_log)
    session.commit()


def get_contact_sync_log():
    contact_sync_log = session.query(ContactSyncLog).order_by(
        ContactSyncLog.sync_time.desc()).all()
    return contact_sync_log
