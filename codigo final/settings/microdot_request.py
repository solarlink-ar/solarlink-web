from microdot_asyncio import Microdot, send_file, redirect, Response
#import urequests as requests
import requests
#import solarlink
#
#solarlink = SolarLink()

##################

app = Microdot()

def connect_to(ssid, passwd):
    """
        Conecta el microcontrolador a la red WIFI
        
        ssid (str): Nombre de la red WIFI
        passwd (str): Clave de la red WIFI
        
        returns (str): Retorna la direccion de IP asignada
    """
    import network
    # Creo una instancia para interfaz tipo station
    sta_if = network.WLAN(network.STA_IF)
    # Verifico que no este conectado ya a la red
    if not sta_if.isconnected():
        # Activo la interfaz
        sta_if.active(True)
        # Intento conectar a la red
        sta_if.connect(ssid, passwd)
        # Espero a que se conecte
        while not sta_if.isconnected():
            pass
        # Retorno direccion de IP asignada
    return sta_if.ifconfig()[0]

def get_connection():
    try:
        # Me conecto a internet
        ip = connect_to("<ssid>", "<password>")
        # Muestro la direccion de IP
        print("Microdot corriendo en IP/Puerto: " + ip + ":5000")
        # Inicio la aplicacion
        app.run()
    
    except KeyboardInterrupt:
        # Termina el programa con Ctrl + C
        print("Aplicación terminada")

INDEX = '''<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
</head>
<form method="POST">
    <center>
        <label for="user">Usuario: </label><br>
        <input type="text" id="user" name="user"><br><br>
        <label for="psswd">Contraseña: </label><br>
        <input type="password" id="psswd" name="psswd"><br><br>
        <input type="submit" value="Continuar">
    </center>
</form>

<center>
    <br><p>Si tenés problemas para iniciar sesión, intentá reestablecer tu contraseña en <a href="https://solarlink.ar/">https://solarlink.ar/</a></p>
    <p id="p1">{content2}</p>
</center>

</html>'''

NULL = ''

LOGIN_FAIL = '''
<br><p>Error al iniciar sesión. Revise su nombre de usuario y/o contraseña.</p>'''

LOGIN_GOOD = '''<!DOCTYPE html>
<html lang="en">

<p>LOGIN SUCCESSFUL. INDIA > PAKISTAN</p>

</html>'''

Response.default_content_type = 'text/html'

@app.route('/')
def index(request):
    return INDEX.format(content2=NULL)

@app.route('/', methods=['POST'])
def auth(request):
    if request.method == 'POST':
        username = request.form["user"]
        password = request.form["psswd"]
        payload = {"username": username, "password": password}
        repost = requests.post("https://solarlink.ar/user/api-login/", data = payload)
        repost.close()
        login_status = repost.json()['login']
        if login_status == True:
            #solarlink.username = username
            #solarlink.password = password
            return LOGIN_GOOD
        else:
            return INDEX.format(content2=LOGIN_FAIL)

app.run()
#get_connection()