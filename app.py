from flask import Flask, request, jsonify, g
from flask_cors import CORS
import izaro as client
import os
import encryption
import json

app = Flask(__name__)
CORS(app)

@app.before_request
def before_request():
    try:
        if request.path == '/login' or request.path == '/health' or request.path == '/favicon.ico' or request.path == '/':
            return
        if 'Authorization' not in request.headers:
            return jsonify({"message": "Missing authorization header"}), 401
        token = request.headers['Authorization']
        if not token:
            return jsonify({"message": "Missing authorization token"}), 401
        encryption_key = os.getenv('ENCRYPTION_KEY')
        if not encryption_key:
            return jsonify({"message": "Missing encryption key"}), 500
        token = encryption.Encryption(encryption_key).decrypt(token)
        if not token:
            return jsonify({"message": "Invalid token"}), 401
        token = json.loads(token)
        g.izaro_cli = client.Izaro(
            token['user'],
            token['password'],
            token['otp'],
            token['wfh'],
            token['web_cookie'],
            token['asp_cookie'],
            token['guid'],
            token['cod_trab'],
            token['sid'],
            token['expiration']
            )
    except Exception:
        return jsonify({"message": "Forbidden"}), 403

@app.route("/login", methods=["POST"])
def login():
    '''
    Login endpoint
    
    This endpoint receives a JSON object with the following fields:
    - user: str
    - password: str
    - otp: str
    - wfh: bool
    '''
    if not request.is_json:
        return jsonify({"message": "Request is not JSON"}), 400
    request_data = request.get_json()
    if 'user' not in request_data or 'password' not in request_data or 'otp' not in request_data or 'wfh' not in request_data:
        return jsonify({"message": "Missing required fields"}), 400
    izaro_cli = client.Izaro(request_data['user'], request_data['password'], request_data['otp'], request_data['wfh'])
    if not izaro_cli.login():
        return jsonify({"message": "Login failed", "error": izaro_cli.error}), 401
    
    cli_settings = vars(izaro_cli)
    del cli_settings['error']
    str_cli_settings = json.dumps(cli_settings)
    encryption_key = os.getenv('ENCRYPTION_KEY')
    token = encryption.Encryption(encryption_key).encrypt(str_cli_settings)

    return jsonify({"message": "Success", "token": token}), 200

@app.route("/clock-ins", methods=["GET"])
def clock_ins():
    '''
    Clock ins endpoint
    '''
    clock_ins = g.izaro_cli.get_historical_clock_ins()
    clock_ins_pending = g.izaro_cli.get_pending_clock_ins()
    return jsonify({"clock_ins": clock_ins, "clock_ins_pending": clock_ins_pending}), 200

@app.route("/clock-in", methods=["POST"])
def clock_in():
    '''
    Clock in endpoint
    
    This endpoint clocks in the user
    '''
    if not g.izaro_cli.clock_in():
        return jsonify({"message": "Clock in failed", "error": g.izaro_cli.error}), 401
    return jsonify({"message": "Success"}), 200

@app.route("/health", methods=["GET"])
def health():
    '''
    Health endpoint
    
    This endpoint returns a JSON object with the message "Healthy"
    '''
    return jsonify({"message": "Healthy"}), 200