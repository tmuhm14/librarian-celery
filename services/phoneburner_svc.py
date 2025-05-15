"""Librarian api_phoneburner"""
# librarian/api_phoneburner.py

import requests
import json
import time
import os


api_token = os.getenv("PHONEBURNER_API_KEY")


def get_all_phoneburner_contacts():
    url = "http://www.phoneburner.com/rest/1/contacts?page_size=500"

    contacts = []
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + api_token,
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data={})
    result = response.json()
    # Append current page contacts; adjust key if your API response structure is different
    contacts.extend(result["contacts"]["contacts"])

    total_pages = result["contacts"]["total_pages"]
    page = 1
    while True:
        url = f'http://www.phoneburner.com/rest/1/contacts?page_size=500&page={page}'
        headers = {
            'Authorization': 'Bearer ' + api_token,
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data={})
        result = response.json()
        contacts.extend(result["contacts"]["contacts"])

        print(f"Page {page} of {total_pages}")
        total_pages = result["contacts"]["total_pages"]
        if page >= total_pages:
            break
        page += 1
    print(f"Total contacts: {len(contacts)}")
    # save to file
    # with open("contacts.json", "w") as f:
    #     json.dump(contacts, f)
    return contacts


def get_contacts_lu(last_update):
    url = f'http://www.phoneburner.com/rest/1/contacts?updated_from={last_update}&page_size=100'

    payload = {}
    headers = {
        'Authorization': 'Bearer ' + api_token,
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text)
    return response.json()


def update_contact_custom_fields(contact_id, custom_field_id, value):
    url = f'http://www.phoneburner.com//rest/1/contacts/{contact_id}/customfields/{custom_field_id}'
    payload = json.dumps({"value": value})
    headers = {
        'Authorization': 'Bearer ' + api_token,
        'Content-Type': 'application/json'
    }
    response = requests.request("PUT", url, headers=headers, data=payload)
    return response.json()


def get_all_contacts_after_update(last_update):
    contacts = []
    page = 1
    while True:
        url = f'http://www.phoneburner.com/rest/1/contacts?updated_from={last_update}&page_size=100&page={page}'
        headers = {
            'Authorization': 'Bearer ' + api_token,
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data={})
        result = response.json()
        # Append current page contacts; adjust key if your API response structure is different
        contacts.extend(result["contacts"]["contacts"])

        total_pages = result["contacts"]["total_pages"]
        if page >= total_pages:
            break
        page += 1

    print(f"Total skippable contacts: {len(contacts)}")
    return contacts


def get_all_phoneburner_folders():
    url = "http://www.phoneburner.com/rest/1/folders"

    payload = {}
    headers = {
        'Authorization': 'Bearer ' + api_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()


def add_contact(record):
    url = "https://www.phoneburner.com/rest/1/contacts"
    payload = json.dumps(record)
    headers = {
        'Authorization': 'Bearer ' + api_token,
        'Content-Type': 'application/json'
    }

    MAX_ATTEMPTS = 5
    attempts = 0
    delay = 1

    # TODO: Raise & catch error instead of quit
    while attempts < MAX_ATTEMPTS:
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 429:
            # Pref. use Retry-After header
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                delay = float(retry_after)
            print(
                f"Rate limit hit (429). Attempt {attempts + 1} of {MAX_ATTEMPTS}. Retrying in {delay} seconds...")
            time.sleep(delay)
            attempts += 1
            delay *= 2
            continue
        elif not response.ok:
            print(
                f"Contact addition failed with status {response.status_code}: {response.text}")
            quit()
        else:
            return response.json()

    print("Max attempts reached. Contact addition failed.")
    quit()


def update_contact(record):
    url = "https://www.phoneburner.com/rest/1/contacts"
    payload = json.dumps(record)
    headers = {
        'Authorization': 'Bearer ' + api_token,
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    return response.json()


def add_folders(company):
    url = "https://www.phoneburner.com/rest/1/folders"
    payload = json.dumps(company)
    headers = {
        'Authorization': 'Bearer ' + api_token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)
    return response.json()
