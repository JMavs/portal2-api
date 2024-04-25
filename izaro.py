import requests
import pyotp
import json
import datetime

class Izaro:
    def __init__(self, user, password, otp, wfh=False, web_cookie=None, asp_cookie=None, guid=None, cod_trab=None, sid=None, expiration=None):
        self.user = user
        self.password = password
        self.otp = otp
        self.wfh = wfh
        self.web_cookie = web_cookie
        self.asp_cookie = asp_cookie
        self.guid = guid
        self.cod_trab = cod_trab
        self.sid = sid
        self.expiration = expiration

        self.error = None
    
    def get_otp(self):
        totp = pyotp.TOTP(self.otp)
        return totp.now()

    def login(self):
        return self.create_session_cookie() and self.make_login_request() and self.make_2fa_request() and self.launch_app() and self.login_launch() and self.validate_user_and_sesion() and self.get_cod_trab()

    def create_session_cookie(self):
        url = "https://portal.saltosystems.com:47123/"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        stored_cookie_session = response.headers['set-cookie'].split(';')[0]
        self.web_cookie = stored_cookie_session
        self.expiration = str(datetime.datetime.now() + datetime.timedelta(minutes=5))

        return True
    
    def refresh_session_if_needed(self):
        if datetime.datetime.strptime(self.expiration, '%Y-%m-%d %H:%M:%S.%f') < datetime.datetime.now():
            return self.login()
        return True
    
    def make_login_request(self):
        url = "https://portal.saltosystems.com:47123/Services/Identification.svc/Login"

        payload = {
            "extendedData": "",
            "izaroblackenv": "",
            "userName": self.user,
            "password": self.password,
            "company": "1",
            "language": "es-ES",
            "remember": "false",
            "NoCache": 0.2712611913192877
        }
        payload = json.dumps(payload, separators=(',', ':'))
        headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'es-ES,es;q=0.9',
        'content-type': 'application/json; charset=UTF-8',
        'cookie': self.web_cookie,
        'origin': 'https://portal.saltosystems.com:47123',
        'referer': 'https://portal.saltosystems.com:47123/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        json_response = response.json()['d']
        self.guid = json_response['GUID']
        if json_response['errorCode'] != 1000:
            self.error = json_response['errorDescription']
            return False
        return True
    
    def make_2fa_request(self):
        url = "https://portal.saltosystems.com:47123/Services/Identification.svc/SecondStepLogin"

        payload = {
            "GUID": self.guid,
            "secondStepPassword": self.get_otp(),
            "language": "es-ES",
            "NoCache": 0.13531394951876852
        }

        payload = json.dumps(payload, separators=(',', ':'))

        headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'es-ES,es;q=0.9',
        'content-type': 'application/json; charset=UTF-8',
        'cookie': self.web_cookie,
        'origin': 'https://portal.saltosystems.com:47123',
        'referer': 'https://portal.saltosystems.com:47123/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        json_response = response.json()['d']
        if json_response['errorCode'] != 0:
            self.error = json_response['errorDescription']
            return False

        return True
    
    def launch_app(self):
        url = "https://portal.saltosystems.com:47123/Services/Loader.svc/LaunchApplication"

        payload = {
            "language": "es-ES",
            "company": "1",
            "extendedData": "",
            "izaroblackenv": "",
            "applicationID": 3,
            "GUID": self.guid,
            "NoCache": 0.2471156899710989
        }
        payload = json.dumps(payload, separators=(',', ':'))
        headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'es-ES,es;q=0.9',
        'content-type': 'application/json; charset=UTF-8',
        'cookie': self.web_cookie,
        'origin': 'https://portal.saltosystems.com:47123',
        'referer': 'https://portal.saltosystems.com:47123/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        self.guid = response.json()['d']['parameters'][0]['Value']
        return True
    
    def login_launch(self):
        url = "https://portal.saltosystems.com:47123/izarob2e/login.aspx"

        payload = "GUID={}".format(self.guid)
        headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'es-ES,es;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': self.web_cookie,
        'origin': 'https://portal.saltosystems.com:47123',
        'referer': 'https://portal.saltosystems.com:47123/',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        self.asp_cookie = response.headers['set-cookie'].split(';')[0]

        # login_user = response.text.split('<input type="hidden" id="usu" value="')[1].split('"')[0]
        self.sid = response.text.split('<input type="hidden" id="sid" value="')[1].split('"')[0]
        return True
    
    def validate_user_and_sesion(self):
        url = "https://portal.saltosystems.com:47123/izarob2e/services/Sesion.svc/ValidarUsrAndSession"

        payload = {
            "login": self.user,
            "sid": self.sid
        }
        payload = json.dumps(payload, separators=(',', ':'))
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json; charset=utf-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://portal.saltosystems.com:47123',
        'Connection': 'keep-alive',
        'Referer': 'https://portal.saltosystems.com:47123/izarob2e/login.aspx',
        'Cookie': "{}; {}".format(self.web_cookie, self.asp_cookie),
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'trailers'
        }

        requests.request("POST", url, headers=headers, data=payload)

        return True
    
    def clock_in(self):
        self.refresh_session_if_needed()

        url = "https://portal.saltosystems.com:47123/izarob2e/services/ControlPr.svc/InsertFichaje"

        payload = {
            "latitud": "",
            "longitud": ""
        }

        if self.wfh:
            payload['codigoMotivo'] = "WFH"
        payload = json.dumps(payload, separators=(',', ':'))
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json; charset=utf-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://portal.saltosystems.com:47123',
        'Connection': 'keep-alive',
        'Referer': 'https://portal.saltosystems.com:47123/izarob2e/Fichar.aspx',
        'Cookie': self.asp_cookie,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'trailers'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.json()['d'] != 1:
            self.error = "Error al fichar"
            return False
        
        return True
    
    def get_cod_trab(self):
        if self.cod_trab:
            return True
        
        url = "https://portal.saltosystems.com:47123/izarob2e/ConsFichajes.aspx"

        payload = {}
        headers = {
        'Cookie': "{}; {}".format(self.web_cookie, self.asp_cookie),
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        self.cod_trab = response.text.split('<input type="hidden" id="codTrab" value="')[1].split('"')[0]

        return True
    
    def get_pending_clock_ins(self):
        self.refresh_session_if_needed()

        url = "https://portal.saltosystems.com:47123/izarob2e/services/ControlPr.svc/GetFichajesPendientesProcesar"

        payload = {
            "empre": "1",
            "codTrab": self.cod_trab
        }
        payload = json.dumps(payload, separators=(',', ':'))
        headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'es-ES,es;q=0.7',
        'content-type': 'application/json; charset=UTF-8',
        'cookie': "{}; {}".format(self.web_cookie, self.asp_cookie),
        'origin': 'https://portal.saltosystems.com:47123',
        'referer': 'https://portal.saltosystems.com:47123/izarob2e/Fichar.aspx',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        all_clock_ins = response.json()['d']

        formated_clock_ins = []
        for clock_in in all_clock_ins:
            formated_clock_ins.append(Check(clock_in['HoraFichaje'], "-", None).to_dict())

        return formated_clock_ins
    
    def get_historical_clock_ins(self):
        self.refresh_session_if_needed()

        today = datetime.date.today()

        url = "https://portal.saltosystems.com:47123/izarob2e/services/ControlPr.svc/GetFichajes"

        payload = {
            "empre": "1",
            "codTrab": self.cod_trab,
            "ejercicio": str(today.year),
            "mes": str(today.month),
        }
        payload = json.dumps(payload, separators=(',', ':'))
        headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'es-ES,es;q=0.7',
        'content-type': 'application/json; charset=UTF-8',
        'cookie': "{}; {}".format(self.web_cookie, self.asp_cookie),
        'origin': 'https://portal.saltosystems.com:47123',
        'referer': 'https://portal.saltosystems.com:47123/izarob2e/ConsFichajes.aspx',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        all_clock_ins = response.json()['d']

        today_clock_ins = [clock_in for clock_in in all_clock_ins if clock_in['Fecha'] == today.strftime('%d/%m/%Y')][0]['Fichajes']

        formated_clock_ins = []
        for clock_in in today_clock_ins:
            formated_clock_ins.append(Check(clock_in['Fichaje'].split('-')[1], clock_in['TipoFichaje'], clock_in['MotivoFichaje']).to_dict())

        return formated_clock_ins
    

class Check:
    def __init__(self, time, type, wfh) -> None:
        self.time = time
        switcher = {
            "E": "Entrada",
            "S": "Salida",
            "2": "Salida automática",
            "-": "No definido",
        }
        self.type = switcher[type]
        if wfh:
            self.wfh = True
        else:
            self.wfh = False

    def to_dict(self):
        return {
            "time": self.time,
            "type": self.type,
            "wfh": self.wfh
        }