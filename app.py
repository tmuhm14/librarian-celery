import os
from flask import Flask, flash, render_template, redirect, request, jsonify
from tasks import add, sync_to_phoneburner

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', "super-secret")
api_key = os.getenv(
    'API_KEY', "wvMxNEJXK0GQ4Jnz7QhR2KUyg2hyxJAQwtqMuiHGnrCVG2Hs8H5pvHFSEz0Qeq7S")


@app.before_request
def before_request():
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
    pd_ref = request.json.get('pd_ref')
    sync_to_phoneburner.delay(pd_ref)
    if not pd_ref:
        return jsonify({'error': 'Missing pd_ref'}), 400
    return jsonify({'message': 'Syncing to Phoneburner'}), 200


@app.route('/add', methods=['POST'])
def add_inputs():
    x = int(request.form['x'] or 0)
    y = int(request.form['y'] or 0)
    add.delay(x, y)
    flash("Your addition job has been submitted.")
    return redirect('/')
