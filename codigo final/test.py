##import urequests as requests
#import requests
#
#data = {"username": "TESTAPENEFAN12", "password": "12345678"}
#
#pete = requests.post("https://solarlink.ar/user/api-login/", json=data )
#
#pete = pete.json()['login']
#
#print(pete)

def get_content(path):
    with open(path) as f:
        raw_lines = f.readlines()
    content = ''.join(raw_lines)
    return content

print(get_content('../microdot_requests/index.html'))