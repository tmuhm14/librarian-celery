import os
from celery import Celery
from celery.utils.log import get_task_logger
from services.sync_svc import sync_to_phoneburner_from_pipedrive
app = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))
logger = get_task_logger(__name__)


198085844
--------------------------------
{'_links': {'self': {'href': '/rest/1/contacts/1198085844/customfields/938026'}}, 'http_status': 200, 'status': 'success', 'customfields': {
    'customfields': [{'custom_field_id': '938026', 'display_name': 'Score Num', 'type_id': '1', 'type_name': 'Text Field', 'display_order': '11', 'value': '2'}]}}
2
--------------------------------
found
2
1198085843
--------------------------------
{'_links': {'self': {'href': '/rest/1/contacts/1198085843/customfields/938026'}}, 'http_status': 200, 'status': 'success', 'customfields': {
    'customfields': [{'custom_field_id': '938026', 'display_name': 'Score Num', 'type_id': '1', 'type_name': 'Text Field', 'display_order': '11', 'value': '2'}]}}
2
--------------------------------
found
2
1198085842
--------------------------------
{'_links': {'self': {'href': '/rest/1/contacts/1198085842/customfields/938026'}}, 'http_status': 200, 'status': 'success', 'customfields': {
    'customfields': [{'custom_field_id': '938026', 'display_name': 'Score Num', 'type_id': '1', 'type_name': 'Text Field', 'display_order': '11', 'value': '2'}]}}
2
--------------------------------
found
2
1198085841
--------------------------------
{'_links': {'self': {'href': '/rest/1/contacts/1198085841/customfields/938026'}}, 'http_status': 200, 'status': 'success', 'customfields': {
    'customfields': [{'custom_field_id': '938026', 'display_name': 'Score Num', 'type_id': '1', 'type_name': 'Text Field', 'display_order': '11', 'value': '2'}]}}
2
--------------------------------
found
2
1198085840
--------------------------------
{'_links': {'self': {'href': '/rest/1/contacts/1198085840/customfields/938026'}}, 'http_status': 200, 'status': 'success', 'customfields': {
    'customfields': [{'custom_field_id': '938026', 'display_name': 'Score Num', 'type_id': '1', 'type_name': 'Text Field', 'display_order': '11', 'value': '2'}]}}
2
--------------------------------
found
2
1198085839
--------------------------------
{'_links': {'self': {'href': '/rest/1/contacts/1198085839/customfields/938026'}}, 'http_status': 200, 'status': 'success', 'customfields': {
    'customfields': [{'custom_field_id': '938026', 'display_name': 'Score Num', 'type_id': '1', 'type_name': 'Text Field', 'display_order': '11', 'value': '2'}]}}
2
--------------------------------
found
2
1198085838
--------


@app.task
def add(x, y):
    logger.info(f'Adding {x} + {y}')
    return x + y


@app.task
def sync_to_phoneburner(pd_ref):
    logger.info(f'Syncing to Phoneburner {pd_ref}')
    sync_to_phoneburner_from_pipedrive(pd_ref)
    return "Synced to Phoneburner"
