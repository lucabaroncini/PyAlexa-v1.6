import datetime
import os
import subprocess
import pyttsx3
import speech_recognition as sr
import pywhatkit
import wikipedia
import webbrowser
import pyjokes
import smtplib
import logging
import time
import re
from ecapture import ecapture as ec
from email.mime.text import MIMEText

ita_lan = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_IT-IT_ELSA_11.0"
en_lan = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"

i = 0
nome_ai = 'sara'
lan = 'italiano'

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('voice', ita_lan)

# Configura il logging
logging.basicConfig(
    filename='assistant.log',
    level=logging.ERROR,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


def set_timer(seconds):
    alexa_talk(f"Timer impostato per {seconds // 60} minuti.")
    time.sleep(seconds)
    alexa_talk("Il tempo è scaduto!")

#FUNZIONE D'INIZIO
def hello():
    if 'italiano' in lan:
        txTalk = 'Ciao, sono ' + nome_ai + ', il tuo assistente vocale'
        alexa_talk(txTalk)
        alexa_talk('Come posso aiutarti?')
    elif 'inglese' in lan:
        txTalk = 'Hi, iam'+ nome_ai +', il tuo assistente vocale'
        alexa_talk(txTalk)
        alexa_talk('how could i help you?')
 
#FUNZIONE DI INVIO EMAIL
def is_valid_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email)

def sendEmail(to):
    if not is_valid_email(to):
        alexa_talk("L'indirizzo email di destinazione non è valido.")
        logging.error(f"Indirizzo email non valido: {to}")
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # Enable low security in gmail
        sender = 'baroncinimantovani@gmail.com'
        #https://myaccount.google.com/apppasswords.
        pw = 'lbpb uukk cejr fnng'
        server.login(sender, pw)
    except smtplib.SMTPAuthenticationError:
        alexa_talk("Errore di autenticazione. Controlla le credenziali dell'email.")
        logging.error("Errore di autenticazione SMTP.")
        return
    except smtplib.SMTPException as e:
        alexa_talk("Errore nel collegamento al server SMTP.")
        logging.error(f"SMTPException: {e}")
        return
        #interpetra messaggio
    listener = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print('Listening...')
            listener.pause_threshold = 0.7
            text = listener.listen(source, timeout=10, phrase_time_limit=5)
            command = listener.recognize_google(text).lower()
            content = command
            alexa_talk("Il messaggio da inviare è: ")
            alexa_talk(content + ',')
            alexa_talk("Vuoi confermare?")
    except sr.RequestError:
        alexa_talk("Servizio di riconoscimento vocale non disponibile.")
        logging.error("Servizio di riconoscimento vocale non disponibile.")
        server.quit()
        return
    except sr.UnknownValueError:
        alexa_talk("Non ho capito il contenuto del messaggio.")
        logging.error("Impossibile capire il contenuto del messaggio.")
        server.quit()
        return
    # Conferma dell'utente
    listener = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print('Listening...')
            listener.pause_threshold = 0.7
            text = listener.listen(source, timeout=10, phrase_time_limit=5)
            command = listener.recognize_google(text).lower()
            print(command)
            if any(confirm in command for confirm in ['si', 'confermo', 'sì', 'conferma']):
                msg = MIMEText(content)
                msg['Subject'] = 'Assistant Email'
                msg['From'] = sender
                msg['To'] = to
                
                server.sendmail(sender,to,msg.as_string())
                server.quit()
                alexa_talk("email inviata con successo")
            else:
                alexa_talk("email non confermata; riprova più tardi!")
    except sr.RequestError:
        alexa_talk("Servizio di riconoscimento vocale non disponibile durante la conferma.")
        logging.error("Servizio di riconoscimento vocale non disponibile durante la conferma.")
    except sr.UnknownValueError:
        alexa_talk("Non ho capito la conferma. Email cancellata.")
        logging.error("Impossibile capire la conferma dell'utente.")
    except smtplib.SMTPException as e:
        alexa_talk("Errore nell'invio dell'email.")
        logging.error(f"SMTPException durante l'invio dell'email: {e}")
    finally:
        server.quit()
        
#FUNZIONE PER CAMBIO LINGUA
def main():
    global i
    global nome_ai
    global lan

    #ITALIANO O INGLESE
    alexa_talk('Per scegliere la lingua italiana devi dire italiano, altrimenti di english')
    engine.setProperty('voice', en_lan)
    alexa_talk('To choose the italian language you must say italiano, else you must say english')
    engine.setProperty('voice', ita_lan)
    listener = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print('Listening...')
            listener.pause_threshold = 1
            gender = listener.listen(source, timeout=10, phrase_time_limit=5)
            command = listener.recognize_google(gender).lower()       
            if 'italiano' in command:
                engine.setProperty('voice', ita_lan)
                alexa_talk("hai impostato la lingua italiana")
                lan = 'italiano'
            elif 'english' in command:
                engine.setProperty('voice', en_lan)
                alexa_talk("You have set the English language")
                lan = 'inglese'
            else:
                engine.setProperty('voice', ita_lan)
                alexa_talk("lingua italiana impostata di default")
                lan = 'italiano'
            command = command.replace(nome_ai, '') 
    except sr.RequestError as e:
        alexa_talk("Servizio di riconoscimento vocale non disponibile.")
        logging.error(f"RequestError in main: {e}")
    except sr.UnknownValueError:
        alexa_talk("Non ho capito la selezione della lingua. Lingua italiana impostata di default.")
        logging.error("UnknownValueError in main: Selezione lingua non riconosciuta.")
    except Exception as e:
        alexa_talk("Si è verificato un errore durante la selezione della lingua.")
        logging.error(f"Exception in main: {e}")


#FUNZIONE PER FAR PARLARE IA 
def alexa_talk(text):
    engine.say(text)
    engine.runAndWait()

#FUNZIONE DI INTERPRETAZIONE 
def accept_command():
    global nome_ai
    global lan
    listener = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print('Listening...')
            listener.pause_threshold = 1
            voice = listener.listen(source, timeout=10, phrase_time_limit=5)
            command = listener.recognize_google(voice, language = 'it-IT' if lan == 'italiano' else 'en-US').lower()
            print(command)
            if nome_ai in command:
                alexa_talk(command)
                command = command.replace(nome_ai, '')
            elif 'siri' in command:
                if lan == 'italiano':
                    alexa_talk('Mi chiamo '+ nome_ai + ' non Siri! Non chiamarmi cosi')
                elif lan == 'inglese':
                    alexa_talk('My name is '+ nome_ai + ' not Siri! Dont call me in that way')

    except sr.RequestError as e:
        alexa_talk("Servizio di riconoscimento vocale non disponibile.")
        logging.error(f"RequestError in accept_command: {e}")
        command = 'miss'
    except sr.UnknownValueError:
        alexa_talk("Non ho capito il comando. Riprova.")
        logging.error("UnknownValueError in accept_command: Comando non riconosciuto.")
        command = 'miss'
    except Exception as e:
        alexa_talk("Si è verificato un errore imprevisto.")
        logging.error(f"Exception in accept_command: {e}")
        command = 'miss'
    return command

#FUNZIONE DI RICHIESTA 
def play_alexa():
    global i
    global lan
    global nome_ai
    command1 = accept_command()
    if command1 != 'miss':
        #INGLESE
        try:
            if lan == 'inglese':
                #Alexa change voice and language
                if 'language' in command1 or 'languages' in command1:
                    main()
                #Alexa playing video on YouTube
                if 'play' in command1 or 'song' in command1:
                    song = command1.replace('play', '').replace('song', '')
                    alexa_talk('playing' + song)
                    pywhatkit.playonyt(song)
                #Alexa telling the time
                elif 'time' in command1:
                    time = datetime.datetime.now().strftime('%I:%M %p')
                    print(time)
                    alexa_talk('The current time is ' + time)
                #ALexa searching for stuff on wikipedia
                elif 'wikipedia' in command1 or  'who is' in command1 or 'tell me about' in command1:
                    alexa_talk('I am saerching on wikipedia')
                    command1 = command1.replace('who is', '').replace('tell me about', '').replace('wikipedia', '')
                    try:
                        info = wikipedia.summary(command1, 3)
                        print(info)
                        alexa_talk(info)
                    except wikipedia.exceptions.DisambiguationError as e:
                        alexa_talk("La tua ricerca è ambigua. Puoi essere più specifico?")
                        logging.error(f"DisambiguationError: {e}")
                    except wikipedia.exceptions.PageError:
                        alexa_talk("Non ho trovato informazioni su questo argomento.")
                        logging.error("PageError: Pagina Wikipedia non trovata.")
                    except Exception as e:
                        alexa_talk("Si è verificato un errore durante la ricerca su Wikipedia.")
                        logging.error(f"Exception durante Wikipedia search: {e}")
                #Alexa telling jokes
                elif 'joke' in command1:
                    alexa_talk(pyjokes.get_joke('en'))
                #open youtube
                elif 'open youtube' in command1:
                    alexa_talk("i am opening youtube\n")
                    webbrowser.open("https://youtube.com")
                #apri google
                elif 'open google' in command1:
                    alexa_talk("i am opening Google\n")
                    webbrowser.open("https://google.com")
                #manda mail
                elif 'email to me' in command1 or 'mail' in command1 :  
                    alexa_talk("what do you want to send?")
                    to = "baroncinimantovani@gmail.com"   
                    sendEmail(to)
                #come stai
                elif 'how are you' in command1:
                    alexa_talk("Mind your own business")
                #nome 
                elif "change your name to" in command1:
                    new_name = command1.replace("change your name to", "").strip()
                    if new_name:
                        nome_ai = new_name
                        alexa_talk(f"My name has been changed to {nome_ai}.")
                    else:
                        alexa_talk("i did not catch the new name.")
                #cerca sul web
                elif 'open' in command1:
                    command1 = command1.replace("open", "").strip()                     
                    webbrowser.open(command1)
                    alexa_talk('Opening' + command1)
                #shutdow pc
                elif 'shutdown' in command1 or 'turn off' in command1 :
                    try:
                        alexa_talk("wait a second ! I'm turning off the computer")
                        subprocess.call(['shutdown', '/s'])
                    except Exception as e:
                        alexa_talk("I cannot turn off the computer.")
                        logging.error(f"Error during the shutdown: {e}")    
                #riavvia il pc
                elif "restart" in command1 or "reboot" in command1:
                    try:
                        alexa_talk("wait a second ! restarting.")
                        subprocess.call(["shutdown", "/r"])
                    except Exception as e:
                        alexa_talk("i could not reboot the computer.")
                        logging.error(f"Errore durante il riavvio: {e}")
                #dove si trova
                elif "where is" in command1:
                    location = command1.replace("where is", "").strip()
                    if location:
                        webbrowser.open(f"https://www.google.nl/maps/place/{location}")
                        alexa_talk(f"Showing where {location} is.")
                    else:
                        alexa_talk("Non ho capito la località.")
                #come ti chiami
                elif "what is your name" in command1 or "your name" in command1:
                    alexa_talk("my first name is" + nome_ai)
                #imposta un timer
                elif "Set a timer of" in command1:
                    if "minutes" in command1 or "minute" in command1:
                        minutes = int(command1.replace("Set a timer of", "").replace("minutes", "").replace("minute", "").strip())
                        set_timer(minutes * 60)
                    elif "seconds" in command1:
                        seconds = int(command1.replace("Set a timer of", "").replace("seconds", "").strip())
                        set_timer(seconds)
                    elif "hours" in command1:
                        hours = int(command1.replace("Set a timer of", "").replace("hours", "").strip())
                        set_timer(hours * 3600)
                #Esci dal programma
                elif 'close' in command1 or 'exit' in command1:
                    alexa_talk('waiting for the program to close...')
                    i = 2
                else:
                    alexa_talk('I did not catch that, please say the command again...')
    #ITALIANO
            elif lan == 'italiano':
                #Alexa change voice and language
                if 'lingua' in command1:
                    main()
                #Alexa playing video on YouTube
                if 'riproduci' in command1 or 'canzone' in command1:
                    song = command1.replace('canzone', '').replace('riproduci','')
                    alexa_talk('riproduco' + song)
                    pywhatkit.playonyt(song)
                #Alexa telling the time
                elif 'ore' in command1 or 'sono' in command1 and not('favore') in command1:
                    time = datetime.datetime.now().strftime('%I:%M %p')
                    print(time)
                    alexa_talk('sono le ' + time)
                #ALexa searching for stuff on wikipedia
                elif 'cerca' in command1 or 'chi è' in command1 or 'parlami di' in command1:
                    alexa_talk('Cerco su wikipedia')
                    command1 = command1.replace('cerca', '')
                    command1 = command1.replace('parlami di', '')
                    try:
                        info = wikipedia.summary(command1, 3)
                        print(info)
                        alexa_talk(info)
                    except wikipedia.exceptions.DisambiguationError as e:
                        alexa_talk("La tua ricerca è ambigua. Puoi essere più specifico?")
                        logging.error(f"DisambiguationError: {e}")
                    except wikipedia.exceptions.PageError:
                        alexa_talk("Non ho trovato informazioni su questo argomento.")
                        logging.error("PageError: Pagina Wikipedia non trovata.")
                    except Exception as e:
                        alexa_talk("Si è verificato un errore durante la ricerca su Wikipedia.")
                        logging.error(f"Exception durante Wikipedia search: {e}")
                #Alexa telling jokes
                elif 'battuta' in command1:
                    alexa_talk(pyjokes.get_joke('it'))
                #apri youtube
                elif 'apri youtube' in command1:
                    alexa_talk("Sto aprendo youtube\n")
                    webbrowser.open("https://youtube.com")
                #apri google
                elif 'apri google' in command1:
                    alexa_talk("Sto aprendo Google\n")
                    webbrowser.open("https://google.com")
                #manda mail
                elif 'email a me' in command1 or 'mail' in command1 :  
                    alexa_talk("Cosa devo dire nell'email?")
                    to = "baroncinimantovani@gmail.com"   
                    sendEmail(to)
                #come stai
                elif 'come stai' in command1:
                    alexa_talk("Fatti i cazzi tuoi")
                #nome 
                elif "cambia il nome in" in command1:
                    new_name = command1.replace("cambia il nome in", "").strip()
                    if new_name:
                        nome_ai = new_name
                        alexa_talk(f"Il mio nome è stato cambiato in {nome_ai}.")
                    else:
                        alexa_talk("Non ho capito il nuovo nome.")
                #cerca sul web
                elif 'apri' in command1:
                    command1 = command1.replace("apri", "").strip()                     
                    webbrowser.open(command1)
                    alexa_talk(command1)
                #shutdow pc
                elif 'spegni' in command1:
                    try:
                        alexa_talk("Aspetta un secondo ! Sto spegnedo il computer")
                        subprocess.call(['shutdown', '/s'])
                    except Exception as e:
                        alexa_talk("non posso spegnere il computer.")
                        logging.error(f"Error during the shutdown: {e}") 
                #riavvia il pc
                elif "riavvio" in command1:
                    try:
                        alexa_talk("Aspetta un secondo! Riavvio in corso.")
                        subprocess.call(["shutdown", "/r"])
                    except Exception as e:
                        alexa_talk("Non sono riuscito a riavviare il computer.")
                        logging.error(f"Errore durante il riavvio: {e}")
                #dove si trova
                elif "dove si trova" in command1:
                    location = command1.replace("dove si trova", "").strip()
                    if location:
                        webbrowser.open(f"https://www.google.nl/maps/place/{location}")
                        alexa_talk(f"Mostro dove si trova {location}.")
                    else:
                        alexa_talk("Non ho capito la località.")
                #come ti chiami
                elif "come ti chiami" in command1:
                    alexa_talk("Mi chiamo" + nome_ai)
                #imposta un timer
                elif "imposta un timer di" in command1:
                    if "minuti" in command1 or "minuto" in command1:
                        minutes = int(command1.replace("imposta un timer di", "").replace("minuti", "").replace("minuto", "").strip())
                        set_timer(minutes * 60)
                    elif "secondi" in command1:
                        seconds = int(command1.replace("imposta un timer di", "").replace("minuti", "").strip())
                        set_timer(seconds)
                    elif "ore" in command1:
                        hours = int(command1.replace("imposta un timer di", "").replace("minuti", "").strip())
                        set_timer(hours * 3600)
                #Esci dal programma
                elif 'esci' in command1 or 'chiudi' in command1:
                    alexa_talk('Chiusura dal programma in corso...')
                    i = 2
                else:
                    alexa_talk('non ho capito un cazzo, ripeti...')
        except Exception as e:
            alexa_talk("Si è verificato un errore durante l'elaborazione del comando.")
            logging.error(f"Exception in play_alexa: {e}")


if __name__ == '__main__':
    wikipedia.set_lang('it')
    hello()
    while i == 0:
        play_alexa()
    
        #print(i)
    if  i == 2:
        print('Chiusura dal programma in corso...')    
        exit()
    

