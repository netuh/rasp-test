import network
import time
import urequests

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Xiaomi 12X', '12345678')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

resp = urequests.get("https://v2.jokeapi.dev/joke/Programming")
joke_dict = resp.json()
print("Here's a joke!")
if 'joke' in joke_dict:
  print(joke_dict['joke'])
else:
  print(joke_dict['setup'])
  print(joke_dict['delivery'])

print()