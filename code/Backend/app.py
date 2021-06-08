from os import wait
from flask.wrappers import Request
from repositories.DataRepository import DataRepository
from serial import Serial, PARITY_NONE
from helpers.lcd import LCDRepository
import time
from RPi import GPIO
import threading
from flask_cors import CORS
from flask import Flask, jsonify, request
from bluedot.btcomm import BluetoothClient
from signal import pause
import time
from flask_socketio import SocketIO, emit, send
from subprocess import check_output
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app)

customEndpoint = '/api/v1'


@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(e)


current_sensor = 0
dict_sensors = {"accelero": "", "pulse": "", "gas": ""}
lcd = LCDRepository()
lcd.init_lcd()
status_neo = True


def lees_data():
    ips = str(check_output(['hostname', '--all-ip-addresses']))
    ips = ips.split(" ")
    lcd.send_instruction(0x1)
    lcd.write_message("Het ip-adres is: ")
    lcd.new_line()
    lcd.write_message("{}".format(str(ips[1])))
    print(ips[1])
    while True:
        print("reading")
        lees_accel()
        time.sleep(4)
        lees_pulse()
        time.sleep(4)
        lees_gas()
        time.sleep(4)


thread = threading.Timer(10, lees_data)
thread.start()


def status_received(data):
    global current_sensor
    global dict_sensors
    line = str(data)[:-2]
    list_sensors = ["accelero", "pulse", "gas"]
    if line != '':
        status = "active"
        dict_sensors[list_sensors[current_sensor]] = status
    else:
        status = "inactive"
        dict_sensors[list_sensors[current_sensor]] = status


def waarde_accel_received(data):
    line = float(data)
    waarde_accelero = line
    DataRepository.insert_waarde_sensor(waarde_accelero, 1)


def waarde_pulse_received(data):
    line = float(data)
    waarde_pulse = line
    DataRepository.insert_waarde_sensor(waarde_pulse, 2)


def waarde_gas_received(data):
    line = float(data)
    waarde_gas = line
    DataRepository.insert_waarde_sensor(waarde_gas, 3)


def lees_status_sensor():
    global current_sensor
    global dict_sensors
    c = BluetoothClient("ESP32test", status_received)
    print("reading sensors")
    list_sensors = ["accelero", "pulse", "gas"]
    for x in range(len(list_sensors)):
        current_sensor = x
        commando = list_sensors[x]
        c.send(commando)
        time.sleep(2)
    c.disconnect()


def lees_accel():
    command = 'accelero'
    c = BluetoothClient("ESP32test", waarde_accel_received)
    c.send(command)
    time.sleep(2)
    c.disconnect()


def lees_pulse():
    command = 'pulse'
    c = BluetoothClient("ESP32test", waarde_pulse_received)
    c.send(command)
    time.sleep(2)
    c.disconnect()


def lees_gas():
    command = 'gas'
    c = BluetoothClient("ESP32test", waarde_gas_received)
    c.send(command)
    time.sleep(2)
    c.disconnect()


def checker(data):
    global status_neo
    line = str(data)
    print(line)
    status_neo = not status_neo
    socketio.emit("B2F_updateNeo", {'Neopixel': status_neo})


@ app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."


@app.route(customEndpoint + '/waardes/<sensor_id>', methods=['GET'])
def get_waardes(sensor_id):
    if request.method == 'GET':
        return jsonify(waarde=DataRepository.read_waardes_sensor(sensor_id))


@app.route(customEndpoint + '/5waardes/<sensor_id>', methods=['GET'])
def get_5waardes(sensor_id):
    if request.method == 'GET':
        return jsonify(waardes=DataRepository.read_5waardes_sensor(sensor_id))


@socketio.on('connect')
def initial_connection():
    print('A new client connect')


@socketio.on('F2B_switchNeo')
def switch_neo():
    command = 'neo'
    c = BluetoothClient("ESP32test", checker)
    c.send(command)
    time.sleep(4)
    c.disconnect()


@socketio.on("F2B_shutdown")
def shut_down():
    subprocess.call(["sudo", "shutdown", "-h", "now"])


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')