#!/usr/bin/env python3
from hermes_python.hermes import Hermes 
from hermes_python.ontology.dialogue import DialogueConfiguration
import requests

MQTT_IP_ADDR = "localhost" 
MQTT_PORT = 1883 
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT)) 


def extraer_noticia():
    url = "http://ep00.epimg.net/rss/elpais/portada.xml"
    response = requests.get(url)
    webContent = response.text.encode('utf-8')
    webContent = webContent.decode()
    webContent = webContent.replace('<item>','@')
    webContent = webContent.split('@')
    titulos = list()
    descripcion = list()
    print(len(webContent))
    for x in webContent:
        x = x.replace('<![CDATA[', '')
        x = x.replace(']]>', '')

        start = x.find('<title>') + 7
        end = x.find('</title>', start)
        titulos.append(x[start:end])
        
        start = x.find('<description>') + 13
        end = x.find('</description>', start)
        descripcion.append(x[start:end])

        result = [titulos, descripcion]
    return result
    
# https://forum.snips.ai/t/interrupt-snips-by-saying-the-hotword/1287/8 de momento no se puede parar el tts.
def intentHandler(hermes, intent_message):
    global N, titulares, descripcion, sentence, i

    
    mensaje = extraer_noticia()
    i = 0
    N = 3
    titulares = [mensaje[0][n:n+N] for n in range(0, len(mensaje[0]), N)]
    descripcion = [mensaje[1][n:n+N] for n in range(0, len(mensaje[1]), N)]
    sentence = 'Éstos son los titulares de hoy: ' + titulares[i]
    i = i + 1
    return hermes.publish_continue_session(intent_message.session_id,  sentence, [])
         

    # hermes.publish_end_session(intent_message.session_id, sentence)                  
def intent_received(hermes, intent_message):
    intentHandler(hermes, intent_message)

def intent_continuar(hermes, intent_message):
    if i < len(titulares):
        sentence = titulares[i]
        i = i + 1
        if i >= len(titulares):
            return hermes.publish_end_session(intent_message.session_id, sentence + '. Esas son todas las noticias')
        else:    
            return hermes.publish_continue_session(intent_message.session_id,  sentence, [])
        

    else:
        return hermes.publish_end_session(intent_message.session_id, 'Esas son todas las noticias')


def intent_stop(hermes, intent_message):
    return hermes.publish_end_session(intent_message.session_id, '')


with Hermes(MQTT_ADDR) as h:
    """dialogue_conf = DialogueConfiguration()                          \
                        .enable_intents(["juancarlos:Cancelar", "juancarlos:Siguiente"])  \


    h.configure_dialogue(dialogue_conf)   
    """
    h.subscribe_intent("DiTitulares", intent_received) \
        .subscribe_intent("Cancelar", intent_stop) \
        .subscribe_intent("Siguiente", intent_continuar) \
        .start()
