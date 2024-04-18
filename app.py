from flask import Flask, request, jsonify
import izaro as client

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    # all responses are json
    if not request.is_json:
        return jsonify({"message": "Request is not JSON"}), 400
    request_data = request.get_json()
    if 'user' not in request_data or 'password' not in request_data or 'otp' not in request_data or 'wfh' not in request_data:
        return jsonify({"message": "Missing required fields"}), 400
    izaro_cli = client.Izaro(request_data['user'], request_data['password'], request_data['otp'], request_data['wfh'])
    if not izaro_cli.login():
        return jsonify({"message": "Login failed", "error": izaro_cli.error}), 401
    if not izaro_cli.clock_in():
        return jsonify({"message": "Clock in failed"}), 401
    return jsonify({"message": "Success"}), 200