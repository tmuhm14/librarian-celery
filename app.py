import os
from flask import Flask, flash, render_template, redirect, request, jsonify
from tasks import add, sync_to_phoneburner
import uuid
from datetime import datetime
from data.repository import create_request_log, update_request_log, get_contact_sync_log
import csv
from pathlib import Path
import requests
import base64

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', "super-secret")
api_key = os.getenv(
    'API_KEY', "wvMxNEJXK0GQ4Jnz7QhR2KUyg2hyxJAQwtqMuiHGnrCVG2Hs8H5pvHFSEz0Qeq7S")


request_id = None
request_time = None
request_type = None
request_data = None
request_status = None
response_time = None
response_status = None


@app.before_request
def before_request():
    global request_id, request_time, request_type, request_data, request_status, response_time, response_status
    request_id = str(uuid.uuid4())
    request_time = datetime.now()
    request_type = request.path
    request_data = request.args
    request_status = 'success'
    response_time = None
    response_status = None
    response_data = None
    create_request_log(request_id, request_type,
                       request_data, request_status, request_time)

    if request.path == '/api/v1/pipedrive/callback' or request.path == '/api/v1/pipedrive/sync/companies' or request.path == '/api/v1/pipedrive/sync/json':
        return
    api_key_param = request.args.get('apikey') or request.args.get('id_key')
    print(api_key_param)
    if api_key_param != api_key:
        return jsonify({'error': 'Unauthorized'}), 401


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/api/v1/phoneburner/sync', methods=['POST'])
def api_sync_to_phoneburner():

    request_data = request.json
    print(f'[DEBUG] request_data: {request_data}')
    if not request_data:

        return jsonify({'error': 'Missing request data'}), 400
    pd_ref = request_data['data']['id']
    if not pd_ref:

        return jsonify({'error': 'Missing pd_ref'}), 400

    print(f'[DEBUG] pd_ref: {pd_ref}')
    sync_to_phoneburner.delay(pd_ref)

    return jsonify({'message': 'Syncing to Phoneburner'}), 200


@app.route('/api/v1/pipedrive/callback', methods=['GET'])
def callback():
    print(f'[DEBUG] Callback args: {request.args}')
    auth_code = request.args.get('code')
    print(f'[DEBUG] Callback auth_code: {auth_code}')
    if not auth_code:
        return jsonify({'error': 'Missing auth code'}), 400

    client_id = 'f767bda5e600a23c'
    client_secret = '10de0ed24692d47dab9de016c7cd6ffaeb331c65'
    url = f"https://oauth.pipedrive.com/oauth/token"

    encoded_credentials = base64.b64encode(
        (f'{client_id}:{client_secret}').encode('utf-8')).decode()
    print(f'[DEBUG] encoded_credentials: {encoded_credentials}')
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': 'https://app-1oya.onrender.com/api/v1/pipedrive/callback',
        'code': auth_code
    }

    print(f'[DEBUG] headers: {headers}')
    print(f'[DEBUG] data: {data}')
    response = requests.post(url, headers=headers, data=data)

    print(f'[DEBUG] response: {response.json()}')
    response_data = response.json()
    access_token = response_data['access_token']
    refresh_token = response_data['refresh_token']
    redirect_uri = response_data['api_domain']

    # redirect to the redirect_uri with the access_token and refresh_token
    return redirect(f"{redirect_uri}/?access_token={access_token}&refresh_token={refresh_token}")


@app.route('/api/v1/pipedrive/sync/companies', methods=['GET'])
def sync_companies():
    print(f'[DEBUG] request: {request}')
    # get auth token from headers
    auth_token = request.headers.get('Authorization')
    print(f'[DEBUG] auth_token: {auth_token}')

    # get access token from auth token

    print('Syncing companies')
    return jsonify({'message': 'Syncing companies'}), 200


@app.route('/api/v1/pipedrive/sync/json', methods=['GET'])
def sync_json():
    # basic auth
    print(f'[DEBUG] request: {request}')
    auth_token = request.headers.get('Authorization')
    print(f'[DEBUG] auth_token: {auth_token}')

    return jsonify({
        "data": [
            {
                "id": 1,
                "header": "GTA 22 Blue Auto",
                "project": "New cars",
                "manufacturer": "Molksvagen LLC",
                "delivery_date": "2021-08-31T07:00:00.000Z",
                "status": {
                    "color": "yellow",
                    "label": "ASSEMBLING"
                },
                "delivery_company": "Jungle Prime",
                "tracking": {
                    "markdown": True,
                    "value": "[Open tracking link](https://pipedrive.com)"
                },
                "note": {
                    "markdown": True,
                    "value": "Meeting next week to sign the [insurance contract](https://pipedrive.com)."
                },
                "extras": [
                    "Cruise control",
                    "Rain detector",
                    "Lane assist"
                ],
                "delivery_cost": {
                    "code": "USD",
                    "value": 2000
                }
            },
            {
                "id": 2,
                "header": "BNW X500",
                "project": "New cars",
                "manufacturer": "Molksvagen LLC",
                "delivery_date": "2021-08-31T07:00:00.000Z",
                "status": {
                    "color": "red",
                    "label": "DELAYED"
                },
                "delivery_company": "Jungle Prime",
                "tracking": {
                    "markdown": True,
                    "value": "[Open tracking link](https://pipedrive.com)"
                },
                "note": {
                    "markdown": True,
                    "value": "Meeting next week to sign the [insurance contract](https://pipedrive.com)."
                },
                "extras": [
                    "Cruise control",
                    "Rain detector",
                    "Lane assist"
                ],
                "delivery_cost": {
                    "code": "USD",
                    "value": 2000
                }
            },
            {
                "id": 3,
                "header": "Dorsche 911",
                "project": "New cars",
                "manufacturer": "Molksvagen LLC",
                "delivery_date": "2021-08-31T07:00:00.000Z",
                "status": {
                    "color": "green",
                    "label": "EN ROUTE"
                },
                "delivery_company": "Jungle Prime",
                "tracking": {
                    "markdown": True,
                    "value": "[Open tracking link](https://pipedrive.com)"
                },
                "note": {
                    "markdown": True,
                    "value": "Meeting next week to sign the [insurance contract](https://pipedrive.com)."
                },
                "extras": [
                    "Cruise control",
                    "Rain detector",
                    "Lane assist"
                ],
                "delivery_cost": {
                    "code": "USD",
                    "value": 2000
                }
            }
        ],
        "external_link": {
            "url": "https://pipedrive.com",
            "label": "Account settings"
        },
        "settings": {
            "url": "https://pipedrive.com"
        }
    }), 200


@app.route('/sync-logs')
def sync_logs():
    sync_logs = get_contact_sync_log()

    logs = []
    for log in sync_logs:
        logs.append({
            "time": log.sync_time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": log.sync_type,
            "contact_id": log.contact_id,
            "pipedrive_id": log.pipedrive_id,
            "phoneburner_id": log.phoneburner_id,
            "name": log.first_name + " " + log.last_name,
            "company": log.folder_name,

        })
    return render_template('sync_logs.html', logs=logs)


@app.route('/sync-org')
def sync_org():
    # Get organization info from request parameters
    org_id = request.args.get('org_id', '')
    org_name = request.args.get('org_name', '')

    return render_template('sync_org.html', org_id="test", org_name="org_name")
