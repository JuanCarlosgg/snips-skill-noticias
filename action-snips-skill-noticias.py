#!/usr/bin/env python3
from hermes_python.hermes import Hermes 
import requests

MQTT_IP_ADDR = "localhost" 
MQTT_PORT = 1883 
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT)) 


def extraer_noticia():
    max = 5
    noticias = ""
    cabeceras = ""
    url = "http://ep00.epimg.net/rss/elpais/portada.xml"
    titulares = list()
    contenidos = list()
    response = requests.get(url)
    webContent = response.text.encode('utf-8')
    webContent = webContent.decode()
    webContent = webContent.replace('<item>','@')
    webContent = webContent.split('@')
    for x in webContent:
        if webContent.index(x) == 0:
            continue
        if webContent.index(x) > max:
            break
        tit = x.replace('<title>','@')
        tit = tit.replace('</title>','@')
        tit = tit.replace('<description>','@')
        tit = tit.replace('</description>','@')
        tit = tit.replace('<![CDATA[', '')
        tit = tit.replace(']]>', '')
        tit = tit.split('@')
        cabeceras += tit[1] + ".\r\n"
        
        noticias += tit[1] + ".\r\n" + tit[3] + ".\r\n"
        result = [cabeceras, noticias]
    return result

def intent_received(hermes, intent_message):
    mensaje = extraer_noticia()
    
    if intent_message.intent.intent_name == 'jaimevegas:DiNoticias':
        sentence = 'Éstas son las noticias de hoy: ' + mensaje[1]
    elif intent_message.intent.intent_name == 'jaimevegas:DiTitulares':
        sentence = 'Éstos son los titulares de hoy: ' + mensaje[0]
                       
    else:
        return
    
    hermes.publish_end_session(intent_message.session_id, sentence)
    
    
with Hermes(MQTT_ADDR) as h:
    h.subscribe_intents(intent_received).start()
