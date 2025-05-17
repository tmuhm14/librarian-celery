"""Librarian api_pipedrive"""
# librarian/api_pipedrive.py
import logging
import requests
import json
import os


api_token = os.getenv("PIPEDRIVE_API_KEY")


def get_person(person):
    print(f"[DEBUG] Getting person: {person}")
    url = f"https://revenuedrivers.pipedrive.com/v1/persons/{person}?api_token={api_token}"

    print(f"[DEBUG] URL: {url}")
    payload = {}
    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    print(f"[DEBUG] Response: {response.json()['data']['id']}")
    return response.json()['data']


def get_latest_pipedrive_contacts_since_last_update(last_update, start=0, limit=500, people=[]):
    # rfc3339 format
    last_update_str = (last_update).strftime("%Y-%m-%dT%H:%M:%S%z")

    contacts_list = []

    url = f"https://revenuedrivers.pipedrive.com/v1/persons?updated_since={last_update_str}&api_token={api_token}"
    print(f"[DEBUG] URL: {url}")
    payload = {}
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, data=payload)
    result = response.json()

    if result["data"]:
        people.extend(result["data"])

    if result["additional_data"]["pagination"]["more_items_in_collection"]:
        people.extend(get_latest_pipedrive_contacts_since_last_update(
            last_update, result["additional_data"]["pagination"]["next_start"], limit, people))

    return people


def get_contacts_data(last_update, start, limit):
    url = f"https://revenuedrivers.pipedrive.com/v1/persons?start={start}&limit={limit}&api_token={api_token}"
    payload = {}
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()


def get_company(company):
    url = f"https://revenuedrivers.pipedrive.com/v1/organizations/{company}?api_token={api_token}"

    payload = {}
    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()


def update_person(person, field_id, field_value):
    url = f"https://revenuedrivers.pipedrive.com/v1/persons/{person}?api_token={api_token}"

    payload = json.dumps({field_id: field_value})
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}

    response = requests.request("PUT", url, headers=headers, data=payload)
    return response.json()


def add_activity(person, org, field_id, field_value, sdate, note_field):
    url = f"https://revenuedrivers.pipedrive.com/api/v2/activities?api_token={api_token}"

    payload = json.dumps({
        "due_date": sdate,
        "type": field_id,
        "subject": field_value,
        "org_id": int(org),
        "note": str(note_field),
        "participants": [
            {
                "person_id": int(person),
                "primary": True
            }
        ]
    })
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


def check_activity(activity):
    url = f"https://api.pipedrive.com/api/v2/activities?ids={activity}&api_token={api_token}"

    payload = {}
    headers = {'Accept': 'application/json'}

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()


def get_organization(start, limit):
    url = f"https://api.pipedrive.com/v1/organizations?filter_id=97&start={start}&limit={limit}&api_token={api_token}"

    payload = {}
    headers = {'Accept': 'application/json'}

    response = requests.request("GET", url, headers=headers, data=payload)

    result = response.json()
    orgs = []

    if result["data"]:
        orgs.extend(result["data"])

    if result["additional_data"]["pagination"]["more_items_in_collection"]:
        orgs.extend(get_organization(
            limit, result["additional_data"]["pagination"]["next_start"]))

    return orgs


def get_all_pipedrive_organizations(start=0, limit=500):
    url = f"https://api.pipedrive.com/v1/organizations?filter_id=97&start={start}&limit={limit}&api_token={api_token}"

    payload = {}
    headers = {'Accept': 'application/json'}

    response = requests.request("GET", url, headers=headers, data=payload)

    result = response.json()
    orgs = []

    if result["data"]:
        orgs.extend(result["data"])

    if result["additional_data"]["pagination"]["more_items_in_collection"]:
        orgs.extend(get_organization(
            limit, result["additional_data"]["pagination"]["next_start"]))

    return orgs


def get_custom_field_options(field_id):
    url = f"https://api.pipedrive.com/v1/customFields/{field_id}/options?api_token={api_token}"

    payload = {}
    headers = {'Accept': 'application/json'}

    response = requests.request("GET", url, headers=headers, data=payload)

    fields = response.json()
    return fields['options'].where(lambda x: x['key'] == field_id)


def get_all_pipedrive_contacts(org, start, limit):
    url = f"https://api.pipedrive.com/v1/organizations/{org}/persons?start={start}&limit={limit}&api_token={api_token}"

    payload = {}
    headers = {'Accept': 'application/json'}

    response = requests.request("GET", url, headers=headers, data=payload)

    result = response.json()
    people = []

    if result["data"]:
        people.extend(result["data"])

    if result["additional_data"]["pagination"]["more_items_in_collection"]:
        people.extend(get_all_pipedrive_contacts(
            org, limit, result["additional_data"]["pagination"]["next_start"]))

    return people


def get_notes(person):
    url = f"https://revenuedrivers.pipedrive.com/v1/notes/?person_id={person}&api_token={api_token}"

    payload = {}
    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()


def add_note(person, content):
    url = f"https://revenuedrivers.pipedrive.com/v1/notes?api_token={api_token}"
    logging.info(f"Adding note w {content}")

    payload = json.dumps({"content": content, "person_id": person})
    headers = {"Accept": "application/json",
               "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)
    logging.info(response.json())
    return response.json()
