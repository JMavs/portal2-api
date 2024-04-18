from flask import Flask, request, jsonify
import izaro as client

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return "<p>Invalid request</p>"
    request_data = request.get_json()
    if 'user' not in request_data or 'password' not in request_data or 'otp' not in request_data or 'wfh' not in request_data:
        return "<p>Invalid request</p>"
    izaro_cli = client.Izaro(request_data['user'], request_data['password'], request_data['otp'], request_data['wfh'])
    izaro_cli.login()
    izaro_cli.clock_in()
    return jsonify({"message": "Login successful", "request_data": request_data})