import os
from flask import Flask, flash, render_template, redirect, request, jsonify
from tasks import add, sync_to_phoneburner
import uuid
from datetime import datetime
from data.repository import create_request_log, update_request_log
import csv
from pathlib import Path

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

    if request.path == '/':
        return
    api_key_param = request.args.get('apikey')
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


@app.route('/add', methods=['POST'])
def add_inputs():
    x = int(request.form['x'] or 0)
    y = int(request.form['y'] or 0)
    add.delay(x, y)
    flash("Your addition job has been submitted.")
    return redirect('/')


@app.route('/sync-logs')
def sync_logs():
    logs = []
    log_file = Path('run_log.csv')

    if log_file.exists():
        with open(log_file, 'r') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                if len(row) >= 4:  # Ensure row has all required fields
                    logs.append({
                        'user_id': row[0],
                        'custom_score': row[1],
                        'pd_ref': row[2],
                        'status': row[3]
                    })

    return render_template('sync_logs.html', logs=logs)
