import json, os, flask, time
from flask import Flask, render_template, abort, request
from peewee import *
from datetime import datetime, timedelta

PASSWORD = '1234' # Update this line
DATABASE_FILE = 'db.sqlite3' # Update this line

## Sentry is optional - Set it up and receive notifications if an exception on the website occours
SENTRY_API_KEY = None # Update this line

if SENTRY_API_KEY is not None:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    sentry_sdk.init(dsn = SENTRY_API_KEY, integrations = [FlaskIntegration()])

app = Flask(__name__)
db = SqliteDatabase(os.path.join(os.path.dirname(os.path.abspath(__file__)), DATABASE_FILE))

class TH(Model):
    class Meta:
        database = db
    device_id = IntegerField()
    temperature = IntegerField()
    relative_humidity = IntegerField()
    timestamp = DateTimeField(default=datetime.now)

# Initialize database
db.create_tables([TH,])
db.close()

@app.before_request
def before_request():
    db.connect()

@app.teardown_request
def teardown__request(response):
    db.close()

@app.route('/', methods=['GET',])
@app.route('/<int:device_id>/', methods=['GET',])
def index(device_id = None):
    '''Present website showing plot of time series data.'''
    distinct_devices = [e.device_id for e in TH.select(TH.device_id).distinct()]
    if len(distinct_devices) == 0:
        return ('No data available', 200)
    if device_id is None:
        device_id = distinct_devices[0]
    return render_template('index.html', devices=distinct_devices, device=device_id)

@app.route('/', methods=['POST',])
def inlet(device_id = None):
    '''Ingest data from ESP8266.'''
    try:
        if request.form['password'] == PASSWORD:
            device_id = request.form['deviceid']
            temperature = request.form['temperature']
            relative_humidity = request.form['humidity']
            TH.insert(device_id=device_id, temperature=temperature, relative_humidity=relative_humidity).execute()
            return ('', 200)
    except:
        pass
    return abort(500)

@app.route('/ajax/<int:device_id>/')
@app.route('/ajax/<int:device_id>/<int:timestamp>/')
def outlet(device_id, timestamp=None):
    '''Outlet for time series data in JSON format.'''
    if timestamp is None:
        # If no reference time is given then fetch a days worth
        current_time = datetime.now(tz=datetime.now().astimezone().tzinfo)
        dt = current_time - timedelta(days=1)
    else:
        # Otherwise, only look for new data
        dt = datetime.fromtimestamp(int(timestamp), tz=datetime.now().astimezone().tzinfo) + timedelta(seconds=1)
    data = TH.select().where( (TH.device_id==device_id) & (TH.timestamp>=dt) ).order_by(+TH.timestamp)
    output = []
    for entry in data:
        output.append([
        int(time.mktime(entry.timestamp.timetuple())),
        entry.temperature,
        entry.relative_humidity,
        ])
    return app.response_class(response=json.dumps(output), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
