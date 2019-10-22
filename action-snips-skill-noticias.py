#!/usr/bin/env python3
from hermes_python.hermes import Hermes 
from hermes_python.ontology.dialogue import DialogueConfiguration
import requests

MQTT_IP_ADDR = "localhost" 
MQTT_PORT = 1883 
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT)) 


def extraer_noticia():
    max = 5
    noticias = ""
    cabeceras = ""
    url = "http://ep00.epimg.net/rss/elpais/portada.xml"
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
    
#Poner un índice en el que se comprueba linea a linea si hay un stop.
# https://docs.snips.ai/articles/platform/dialog/frame-based-dm
# https://github.com/snipsco/hermes-protocol/tree/develop/platforms/hermes-javascript#api
# https://github.com/MrJohnZoidberg/Snips-Einkaufsliste/blob/master/action-ShoppingList.py
# https://forum.snips.ai/t/interrupt-snips-by-saying-the-hotword/1287/8 de momento no se puede parar el tts.
def intentHandler(hermes, intent_message, mensaje):
    if intent_message.intent.intent_name == 'jaimevegas:DiNoticias':
        hermes.publish_end_session(intent_message.session_id,  'Éstas son las noticias de hoy: '+ mensaje[1])
        """
        contenido = mensaje[1]
        for i in len(contenido):
            hermes.publish_continue_session(intent_message.session_id, mensaje[1][i], [])
            intent_stop(hermes,intent_message)
        hermes.publish_end_session(intent_message.session_id, '')
        """
    elif intent_message.intent.intent_name == 'jaimevegas:DiTitulares':
        hermes.publish_end_session(intent_message.session_id,  'Éstos son los titulares de hoy: ' + mensaje[0])
        """titulares =  mensaje[0]
        for i in len(titulares):
            hermes.publish_continue_session(intent_message.session_id, mensaje[1][i], [])
            intent_stop(hermes,intent_message)
        hermes.publish_end_session(intent_message.session_id, '')
        """
    else:
        return 

    # hermes.publish_end_session(intent_message.session_id, sentence)                  
def intent_received(hermes, intent_message):
    mensaje = extraer_noticia()
    intentHandler(hermes, intent_message, mensaje)
     

def intent_stop(hermes, intent_message):
    #if intent_message.intent.intent_name == 'juancarlos:Cancelar':
    hermes.publish_end_session(intent_message.session_id, '')


with Hermes(MQTT_ADDR) as h:
    #dialogue_conf = DialogueConfiguration().enable_intent("Stop")  
    
    #h.configure_dialogue(dialogue_conf)                   
    h.subscribe_intent("jaimevegas:DiTitulares", intent_received) \
        .subscribe_intent("jaimevegas:DiNoticias", intent_received) \
        .subscribe_intent("juancarlos:Cancelar", intent_stop) \
        .start()
