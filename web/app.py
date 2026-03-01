from flask import Flask, render_template
import paho.mqtt.client as mqtt
import threading
import requests
import queue
from flask import Response, stream_with_context

app = Flask(__name__)

# MQTT configuration (should match hardware/config.h)
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "epic-blueprint/sensor/distance"
MQTT_TOPIC_SPEED = "epic-blueprint/sensor/speed"

# store the most recent speed (m/s)
latest_speed = None

# simple list of queues for server‑sent events subscribers
_sse_subscribers = []


# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    # only need speed topic now (published per step)
    client.subscribe(MQTT_TOPIC_SPEED)

def on_message(client, userdata, msg):
    global latest_speed
    try:
        value = float(msg.payload.decode())
    except ValueError:
        return

    latest_speed = value

    # push to all SSE subscribers
    payload = str(latest_speed)
    for q in list(_sse_subscribers):
        q.put(payload)

# set up client and start background loop
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()

def get_mbta_train_info():
    start_url = 'https://api-v3.mbta.com/predictions?filter[stop]=place-pktrm&filter[route]=Red&sort=departure_time&filter[direction_id]=0'
    end_url = 'https://api-v3.mbta.com/predictions?filter[stop]=place-dwnxg&filter[route]=Red&sort=departure_time&filter[direction_id]=0'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        start = requests.get(start_url, headers=headers)
        end = requests.get(end_url, headers=headers)

        # if success
        if start.status_code == 200:
            
            # .json for converting to dicts and lists python
            depart = start.json()
            arrive = end.json()
            train_id = depart['data'][0].get('relationships', {}).get('trip', {}).get('data', {}).get('id')
            dep_time = depart['data'][0].get('attributes', {}).get('departure_time')
            arr_time = None

            print(f"Train {train_id} departing Park Street at: {depart['data'][0].get('attributes', {}).get('departure_time')}")

            # Loop through the Downtown Crossing trains to find exact train
            for train in arrive['data']:
                current_id = train.get('relationships', {}).get('trip', {}).get('data', {}).get('id')
                
                if current_id == train_id:
                    arr_time = train.get('attributes', {}).get('arrival_time')
                    print(f"Train {train_id} arriving at Downtown Crossing: {arr_time}")
                    break
            # Calculate the difference in seconds
            travel_time_seconds = None
            if dep_time and arr_time:
                dep_dt = datetime.fromisoformat(dep_time)
                arr_dt = datetime.fromisoformat(arr_time)
                # .total_seconds() returns a float, so we convert to int
                travel_time_seconds = int((arr_dt - dep_dt).total_seconds())

            return {
                "status": "success",
                "train_id": train_id,
                "travel_time_seconds": travel_time_seconds
            }

        else:
            print(f"Failed to retrieve data. Status code: {start.status_code}")
    except Exception as e:
        return {"error": str(e)}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/distance')
def get_distance():
    """Return the most recent speed (m/s) as JSON."""
    return {"speed": latest_speed}


@app.route('/stream')
def stream():
    """Server‑sent events stream of distance updates."""
    def event_stream():
        q = queue.Queue()
        _sse_subscribers.append(q)
        try:
            while True:
                data = q.get()
                yield f"data: {data}\n\n"
        except GeneratorExit:
            _sse_subscribers.remove(q)
    headers = {"Content-Type": "text/event-stream", "Cache-Control": "no-cache"}
    return Response(stream_with_context(event_stream()), headers=headers)

@app.route('/api/train')
def train_schedule():
    return get_mbta_train_info()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
