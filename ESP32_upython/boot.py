
def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect('Red Alumnos', '')
        while not wlan.isconnected():
            pass
do_connect()