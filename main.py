import network
from umqtt.simple import MQTTClient
import urequests
from machine import Pin, PWM
import dht
import ujson
import utime

# Hardware
servo = PWM(Pin(13), freq=50)
sensor = dht.DHT22(Pin(4))

# IFTTT
IFTTT_KEY = "YOUR_IFTTT_KEY_HERE"

# State
fan_state = False
mode = "auto"
TEMP_MAX = 35
last_publish = 0
last_alert = 0
mqtt = None  # sera défini après connect

def servo_on():
    global fan_state
    fan_state = True
    servo.duty(120)
    print("❄️ Fan ON")

def servo_off():
    global fan_state
    fan_state = False
    servo.duty(40)
    print("✓ Fan OFF")

def send_ifttt(temp, hum, seuil):
    try:
        url = "https://maker.ifttt.com/trigger/temp_alert/with/key/{}".format(IFTTT_KEY)
        data = ujson.dumps({
            "value1": str(temp),
            "value2": str(hum),
            "value3": str(seuil)
        })
        headers = {"Content-Type": "application/json"}
        r = urequests.post(url, data=data, headers=headers)
        print("→ IFTTT OK! Response:", r.status_code)
        r.close()
    except Exception as e:
        print("IFTTT error:", e)

def publish_now(temp=None, hum=None):
    global last_publish
    try:
        if temp is None:
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
        payload = ujson.dumps({
            "temperature": temp,
            "humidity": hum,
            "fan_state": fan_state,
            "mode": mode,
            "threshold": TEMP_MAX
        })
        mqtt.publish("v1/devices/me/telemetry", payload)
        last_publish = utime.ticks_ms()
        print("→ Publié | mode:", mode, "| fan:", fan_state)
    except Exception as e:
        print("Publish error:", e)

def on_message(topic, msg):
    global mode, TEMP_MAX
    try:
        data = ujson.loads(msg)
        method = data.get("method", "")
        params = data.get("params", False)
        print("CMD:", method, "→", params)

        if method == "setState":
            if params == True or params == 1:
                mode = "manual_on"
                servo_on()
            else:
                mode = "manual_off"
                servo_off()

        elif method == "setAuto":
            mode = "auto"
            # Apply auto logic immediately
            try:
                sensor.measure()
                temp = sensor.temperature()
                hum = sensor.humidity()
                if temp > TEMP_MAX:
                    servo_on()
                else:
                    servo_off()
                # Publish immediately so switch updates instantly
                publish_now(temp, hum)
            except Exception as e:
                print("Auto apply error:", e)
            return

        elif method == "setThreshold":
            TEMP_MAX = float(params)
            print("→ Seuil:", TEMP_MAX)

        # Publish immediately after any command
        publish_now()

    except Exception as e:
        print("Error:", e)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("Wokwi-GUEST", "")
    while not wlan.isconnected():
        utime.sleep(0.5)
        print(".")
    print("✓ WiFi OK")

def connect_mqtt():
    client = MQTTClient(
        "ESP32_TempHum",
        "mqtt.thingsboard.cloud",
        port=8883,
        user="YOUR_DEVICE_TOKEN_HERE",
        password="",
        ssl=True,
        ssl_params={"server_hostname": "mqtt.thingsboard.cloud"}
    )
    client.set_callback(on_message)
    client.connect()
    client.subscribe("v1/devices/me/rpc/request/+")
    print("✓ MQTT TLS OK")
    return client

# Start
connect_wifi()
mqtt = connect_mqtt()
servo_off()

while True:
    try:
        mqtt.check_msg()

        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        # 3 modes logic
        if mode == "auto":
            if temp > TEMP_MAX:
                servo_on()
            else:
                servo_off()
        elif mode == "manual_on":
            servo_on()
        elif mode == "manual_off":
            servo_off()

        print("Temp:", temp, "| Hum:", hum,
              "| Mode:", mode, "| Fan:", fan_state,
              "| Seuil:", TEMP_MAX)

        # IFTTT alert toutes les 60 secondes
        now = utime.ticks_ms()
        if temp > TEMP_MAX:
            if utime.ticks_diff(now, last_alert) > 60000:
                last_alert = now
                print("→ Sending IFTTT alert...")
                send_ifttt(temp, hum, TEMP_MAX)

        # Publish toutes les 5 secondes
        if utime.ticks_diff(now, last_publish) > 5000:
            publish_now(temp, hum)

    except Exception as e:
        print("Error:", e)
        utime.sleep(1)

    utime.sleep(2)