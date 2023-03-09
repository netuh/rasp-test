from imu import MPU6050

import network
import socket
import time

from machine import Pin, I2C

# Configuração Inicial
led = Pin("LED", Pin.OUT)
html = """<!DOCTYPE html>
<html>
    <head>
        <title>Page Title</title>
        <meta http-equiv="refresh" content="10">
    </head>
    <body> 
        <h1>Monitor do sensor</h1>
        <p>%s</p>
    </body>
</html>
"""
ssid = 'ASUS_RPN12'
password = '12345678'


def start_acce():
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    imu = MPU6050(i2c)
    return imu


def start_server():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print('listening on', addr)
    return s

# Listen for connections


imu = start_acce()
s = start_server()
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        print(request)
        ax = round(imu.accel.x)
        ay = round(imu.accel.y)
        az = round(imu.accel.z)
        print("ax=", ax)
        print("ay=", ay)
        print("az=", az)
        if ax == 0 and ay == 0 and az == 1:
            stateis = "Est\'a no plano!"
        elif ax == 0 and az == 0 and (ay == 1 or ay == -1):
            stateis = "Est\'a em peh!"
        elif ax == 0 and ay == 0 and az == -1:
            stateis = "Est\'a de cabeca para baixo!"
        else:
            stateis = "Est\'a torto!"

        response = html % stateis

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')
