from flask import Flask, render_template, request
import paho.mqtt.client as mqtt
import threading
import queue
from flask import Response, stream_with_context

app = Flask(__name__)

# MQTT configuration (should match hardware/config.h)
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/distance"

# store the most recent reading
latest_distance = None
# whether the most recent value counts as a step
step_detected = False

# simple list of queues for server‑sent events subscribers
_sse_subscribers = []

# threshold (deadband) around zero in centimeters
DEAD_BAND = 4.0  # adjust to taste, distance <= this is treated as a step

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global latest_distance, step_detected
    try:
        latest_distance = float(msg.payload.decode())
        # decide whether this qualifies as a step
        step_detected = abs(latest_distance) <= DEAD_BAND
        # notify any active SSE clients with both values
        payload = f"{latest_distance},{int(step_detected)}"
        for q in list(_sse_subscribers):
            q.put(payload)
    except ValueError:
        pass

# set up client and start background loop
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()

@app.route('/')
def index():
    # pass the latest MQTT value to the template
    return render_template('index.html', distance=latest_distance)

@app.route('/distance')
def get_distance():
    """Return the most recent reading and step flag as JSON."""
    return {"distance": latest_distance, "step": step_detected}


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


@app.route('/api/raw', methods=['POST'])
def raw_data():
    data = request.get_json()
    print(f"Distance received: {data}")
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)