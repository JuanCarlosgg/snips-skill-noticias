#!/usr/bin/env python3
from hermes_python.hermes import Hermes 
from hermes_python.ontology.dialogue import DialogueConfiguration
import requests

MQTT_IP_ADDR = "localhost" 
MQTT_PORT = 1883 
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT)) 


def extraer_noticia():
    noticias = ""
    cabeceras = ""
    url = "http://ep00.epimg.net/rss/elpais/portada.xml"
    response = requests.get(url)
    webContent = response.text.encode('utf-8')
    webContent = webContent.decode()
    webContent = webContent.replace('<item>','@')
    webContent = webContent.split('@')
    for x in webContent:
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
    
# https://forum.snips.ai/t/interrupt-snips-by-saying-the-hotword/1287/8 de momento no se puede parar el tts.
def intentHandler(hermes, intent_message):
    global N, titulares, descripcion, sentence, i

    if intent_message.intent.intent_name == 'jaimevegas:DiTitulares': 
        mensaje = extraer_noticia()
        i = 0
        N = 3
        titulares = [mensaje[0][n:n+N] for n in range(0, len(mensaje[0]), N)]
        descripcion = [mensaje[1][n:n+N] for n in range(0, len(mensaje[1]), N)]
        sentence = 'Éstos son los titulares de hoy: ' + titulares[i]
        i = i + 1
        hermes.publish_continue_session(intent_message.session_id,  sentence, ['juancarlos:Cancelar', 'juancarlos:Siguiente'])
    else:
        hermes.publish_end_session(intent_message.session_id, '')
         

    # hermes.publish_end_session(intent_message.session_id, sentence)                  
def intent_received(hermes, intent_message):
    intentHandler(hermes, intent_message)

def intent_continuar(hermes, intent_message):
    if i < len(titulares):
        sentence = titulares[i]
        i = i + 1
        hermes.publish_continue_session(intent_message.session_id,  sentence, ['juancarlos:Cancelar', 'juancarlos:Siguiente'])
    else:
        hermes.publish_end_session(intent_message.session_id, 'Esas son todas las noticias')


def intent_stop(hermes, intent_message):
    hermes.publish_end_session(intent_message.session_id, '')


with Hermes(MQTT_ADDR) as h:
    dialogue_conf = DialogueConfiguration()                          \
                        .enable_intents(["juancarlos:Cancelar", "juancarlos:Siguiente"])  \


    h.configure_dialogue(dialogue_conf)      
    h.subscribe_intent("jaimevegas:DiTitulares", intent_received) \
        .start()
