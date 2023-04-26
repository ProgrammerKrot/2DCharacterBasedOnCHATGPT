import pygame  #loading libs
import openai  #for chatgpt and dalle
import connectdalle #import func with dalle's response
import urllib.request #lib for downloading files from url
import os
import wave  #audio
import pyaudio #audio
import threading #multithreading
import queue #support multithreading
import speech_recognition as sr
import json  #for json file with session history
import pyttsx3 #text to speech
from ultralytics import YOLO  #object detection
import cv2 #camera

# create instance of tts and queue
engine = pyttsx3.init()
image_queue = queue.Queue()


def load_image(prompt):
    # generating URL of image
    image_url = connectdalle.imagegenai("Asuka Langley Soryu " + prompt)
    print(image_url)
    # file path
    filename = "my_image.png"

    def reporthook(blocknum, blocksize, totalsize):  #func for showing progress of loading image in console
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = readsofar * 100 / totalsize
            print(f"Downloaded {readsofar} of {totalsize} bytes ({percent:.2f}%)\r", end="")

    urllib.request.urlretrieve(image_url, filename, reporthook=reporthook) #request for url to download file
    try:
        with open(filename, 'rb') as f:
            image_data = pygame.image.load(f)
    except pygame.error:
        print("Cannot load image:", filename)
        return None

    #below we just blit image in pygame window
    image_data = resize(image_data, 400)
    dog_rect = image_data.get_rect(
        bottomright=(425, 600))
    screen.blit(image_data, dog_rect)





# set properties of language and windows speech voice
engine.setProperty('voice', 'english')  # установить язык голоса
engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')


voice_text = ""
#class for listening what is user saying while he is pressing the button
class AudioRecorder:
    def __init__(self): #init class and define values
        self.chunk = 1024      #settings of input audio (how to decode it)
        self.sample_format = pyaudio.paInt16
        self.channels = 1
        self.fs = 44100
        self.frames = []
        self.recording = False
        self.stream = None
        self.thread = None
        self.output_file = "recorded_audio.wav"  # default output file name

    def start_recording(self):
        self.stream = pyaudio.PyAudio().open(format=self.sample_format, channels=self.channels,
                                             rate=self.fs, frames_per_buffer=self.chunk, input=True)
        self.recording = True
        self.frames = []
        self.thread = threading.Thread(target=self.record)  #recording in background (while it is working, program continue doing its things
        self.thread.start()
        print("Recording started")

    def stop_recording(self):
        self.recording = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close() #stop thread and close audio stream

        # Write recorded frames to a WAV file
        with wave.open(self.output_file, 'wb') as f:
            f.setnchannels(self.channels)
            f.setsampwidth(pyaudio.PyAudio().get_sample_size(self.sample_format))
            f.setframerate(self.fs)
            f.writeframes(b"".join(self.frames))

        print(f"Saved recorded audio to file: {os.path.abspath(self.output_file)}")

    def record(self):
        while self.recording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)
            print(f"Recorded {len(data)} bytes of audio") #info about how many information we spended on each frame

audio_recorder = AudioRecorder()
button_pressed = False
r = sr.Recognizer()

#func that will be executed in the main thread while the button is prressed
def listen_while_button_pressed():
    global button_pressed, voice_text
    button_pressed = True
    audio_recorder.start_recording()
    while button_pressed:
        pass
    audio_recorder.stop_recording()
    audio = sr.AudioData(b"".join(audio_recorder.frames), audio_recorder.fs,
                         pyaudio.get_sample_size(audio_recorder.sample_format))
    try:
        voice_text = r.recognize_google(audio, language="en") #google recognize users speech
        print("Done!")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    button_pressed = False



# making image fitin screen
def resize(image, screen_height):
    original_width, original_height = image.get_size()
    aspect_ratio = original_width / original_height
    new_height = int(screen_height)
    new_width = int(new_height * aspect_ratio)
    image = pygame.transform.scale(image, (new_width, new_height))
    return image


#api keys
openai.api_key = "YOUR TOKEN"
# Set up the drawing window


#we should set videodriver to make our window more smooth
os.environ['SDL_VIDEODRIVER'] = 'windows'


pygame.init() #pygame initializaton
screen = pygame.display.set_mode([800, 600]) #settings of screen

#yolo settings
model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)



camera = cv2.VideoCapture(0) #camera starts
#dictionary with all objects which can be detected
my_dict = {0: 'interlocutor', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'}
detected_objects = []
prev_detected_obj = []
def detect_objects():
    global detected_objects

    while camera.isOpened():
        #read a frame
        ret, frame = camera.read()
        results = model.predict(source=frame, conf=0.5, show=True)
        # and getting results of detections
        for result in results:
            tensorlist = (result.boxes.data).tolist()
            #search through the dictionary to matches
            objects = [my_dict[int(obj[-1])] for obj in tensorlist]
            detected_objects.extend(objects)


# some castomization
background = pygame.image.load("backgroundtest.png") #background
#emotions
sarcastic_vibe = pygame.image.load("sarcastic.png")
sarcastic_vibe = resize(sarcastic_vibe, 600)
neutral_vibe = pygame.image.load("neutral.png")
neutral_vibe = resize(neutral_vibe, 600)
unknown = pygame.image.load("neznau.png")
unknown = resize(unknown, 600)
annoy_vibe = pygame.image.load("razdrazenie.png")
annoy_vibe = resize(annoy_vibe, 600)
laught = pygame.image.load("smeh.png")
laught = resize(laught, 600)
smile = pygame.image.load("ulybka.png")
smile = resize(smile, 600)
elation = pygame.image.load("vostorg.png")
elation = resize(elation, 600)
prev_emo = ""

prev_chat_response0 = ""

# all texts settings
font = pygame.font.SysFont('font.otf', 24)
# hight of one line
line_height = font.get_linesize()
x = 460
y = 400
text_rect = pygame.Rect(441, 475, 354, 119)

#loading screen
loading_screen_image = pygame.image.load("loading_screen.png")
screen.blit(loading_screen_image, (0, 0))
pygame.display.flip()

# texts colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (51, 102, 0) #(30, 90, 20)
red = (102, 51, 51) #(105, 33, 57)

red_color = (255, 0, 0)
green_color = (0, 255, 0)


#buttons
#voice button
bvoice_rect = pygame.Rect(3, 3, 100, 100)
bvoice_surf = pygame.Surface(bvoice_rect.size)
voicebtn = pygame.image.load("voicebtn.png")
bvoice_surf.blit(voicebtn, (3, 3))
#dalle button
binoff_rect = pygame.Rect(563, 7, 100, 50)
binoff_surf = pygame.Surface(binoff_rect.size)
pygame.draw.rect(binoff_surf, red_color, binoff_rect)
pygame.draw.rect(binoff_surf, green_color, (0, 0, binoff_rect.width/2, binoff_rect.height))
pygame.draw.rect(binoff_surf, red_color, (binoff_rect.width/2, 0, binoff_rect.width/2, binoff_rect.height))
count = 1
#tts button
btts_rect = pygame.Rect(113, 3, 100, 100)
btts_surf = pygame.Surface(btts_rect.size)
ttsbtn = pygame.image.load("ttsoff.png")
btts_surf.blit(ttsbtn, (3, 3))


# list oof emotions

textemo = ["neutral", "dont understand", "annoyed", "funny", "smile", "elation", "sarcastic"]

need_input = False
need_sounds = False
show_text = ""
input_text = ""
all_texts = []
messages = []

#content with "rules" of the game for chatGPT
anothercontent = "Lets play in a game: ill give you a character and you will pretend that you are him (answering like " \
                 "him, interact like him, so do whatever what he would like to do). I give you after // that youre see in the moment. I aslo give you something like " \
                 "layout of your answers. hint for layout: Where i typed «YOURWORDS»,you should type answer of your " \
                 "character, where i typed «ACTIONS», you always should type one of the avaleible emotions: neutral, " \
                 "dont understand, annoyed, funny, smile, elation, sarcastic. YOU CANNOT USE ANY DIFFERENT EMOTIONS OR COMBINE IT IF I DONT SAY TO YOU DO THAT. For example: Me: Hello! You: Hello!//neutral. Layout: " \
                 "Asuka: *YOURWORDS* //ACTIONS. ALSO, i can say you to discribe what you character do without any prohibitions by saying to yuo word DESCRIBE. And so, " \
                 "here is a cherecter: Asuka from anime Evangelion. Shes love sarcasm and making joke every time when " \
                 "somebody trying to offense her. Also she love programmin, but she dont want to " \
                 "demonstrate it. Also she pretty often making a joke about her interlocutor. "

# history loading if file with history exists
try:
    with open("session_history.json", "r") as f:
        messages = [{"role": "system", "content": "Just a bot"}, {"role": "user", "content": anothercontent}]
        messages.extend(json.load(f))
        beginlen = len(messages)
except FileNotFoundError:
    messages = [
        {"role": "system", "content": "Just a bot"},
        # here i just give a name to this session or something (not important)
        {"role": "user", "content": anothercontent}
        # and here i give to chatgpt a content (rules of the game, do you remember?))
    ]


completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0.9,
                                          max_tokens=100)  # this is options of chatgpt: first two i guess you
# understand and second two: temperature - bot's "creativity" and tokens - max count of letters (1 token != 1 symbol)
chat_response = completion.choices[0].message.content  # applying and sending options of chatgpt
messages.append({"role": "assistant", "content": chat_response})

# Running thread with object detection
thread = threading.Thread(target=detect_objects)
thread.daemon = True
thread.start()


running = True
while running:
    #getting mouse position and its status
    mouse_pos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()

    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    #blit buttons
    screen.blit(bvoice_surf, bvoice_rect)
    screen.blit(binoff_surf, binoff_rect)
    screen.blit(btts_surf, btts_rect)

    #avoiding many "fantom" detected project in list
    if len(detected_objects) >= 1:
        prev_detected_obj = detected_objects
    elif len(detected_objects) >= 5:
        detected_objects = list(set(detected_objects))
        if detected_objects >= 5:
            detected_objects = detected_objects[:4]
    else:
        detected_objects = prev_detected_obj


    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #if mouseb button was pressed and mouse pos on dalle switcher?
        if event.type == pygame.MOUSEBUTTONDOWN:
            if binoff_rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]:
                    temp_color = red_color
                    red_color = green_color
                    green_color = temp_color

                    # switching of dalle button (redrawing it)
                    pygame.draw.rect(binoff_surf, red_color, binoff_rect)
                    pygame.draw.rect(binoff_surf, green_color, (0, 0, binoff_rect.width / 2, binoff_rect.height))
                    pygame.draw.rect(binoff_surf, red_color,
                                     (binoff_rect.width / 2, 0, binoff_rect.width / 2, binoff_rect.height))
                    count += 1


        #mouse pressed and position on voice button
        if event.type == pygame.MOUSEBUTTONDOWN:
            if bvoice_rect.collidepoint(mouse_pos):
                print("tap")
                button_pressed = True
                #launching thread with voice listening
                listen_thread = threading.Thread(target=listen_while_button_pressed)
                listen_thread.start()
        # ending thread, because user release button
        elif event.type == pygame.MOUSEBUTTONUP:
            if button_pressed and bvoice_rect.collidepoint(mouse_pos):
                button_pressed = False
                listen_thread.join()
                content = voice_text
                all_texts.append(voice_text)
                # if count % 2 = 0, then dalle switcher is on, if not dalle switcher is off
                # differences only between two completion
                if count % 2 == 1:
                    messages.append(
                        {"role": "user",
                            "content": content + f"//Asuka sees: {set(detected_objects)} " + "(Stay in character, now your actions always after this // symbol, maximum 50 letters, ONLY THESE EMOTIONS WITHOUT COMBO (EMOTION + EMOTION): neutral,"
                                                  "dont understand, annoyed, funny, smile, elation, sarcastic"})
                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.9,
                        max_tokens=100
                    )
                    chat_response = completion.choices[0].message.content
                    messages.append({"role": "assistant", "content": chat_response})
                    fin_chat_response = chat_response.split("//")
                    all_texts.append(fin_chat_response[0])

                    print(fin_chat_response[1])
                else:
                    messages.append(
                        {"role": "user",
                         "content": content + f"//Asuka sees: {set(detected_objects)} " + "(Stay in character, now after // symbol you should DESCRIBE what is your character doing"})
                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.9,
                        max_tokens=100
                    )
                    chat_response = completion.choices[0].message.content
                    messages.append({"role": "assistant", "content": chat_response})
                    fin_chat_response = chat_response.split("//")
                    #then user turn on text to speech for asuka, it will transfer it into speech
                    if need_sounds == True:
                        engine.say(fin_chat_response[0])
                        engine.runAndWait()

                    # asukas answer will be show on screen later
                    all_texts.append(fin_chat_response[0])
                    print(fin_chat_response[1])

        #same sending request to asuka but by keyboard
        if need_input and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                print(input_text + show_text)
                content = input_text + show_text
                if count % 2 == 1:
                    print(content + f"//Asuka sees: {detected_objects} "+ "(Stay in character, now your Layout: *YOURWORDS* //ACTIONS, actions always after "
                                                  "this // symbol, try answer short, ONLY THESE EMOTIONS WITHOUT COMBO ("
                                                  "EMOTION + EMOTION): neutral,"
                                                  "dont understand, annoyed, funny, smile, elation, sarcastic")
                    messages.append(
                        {"role": "user",
                         "content": content + f"//Asuka see: {detected_objects} "+ "(Stay in character, Layout: *YOURWORDS* //ACTIONS, actions always after "
                                              "this // symbol, try answer short, ONLY THESE EMOTIONS WITHOUT COMBO AND SYMBOLS AFTER THAT ("
                                              "EMOTION + EMOTION): neutral,"
                                              "dont understand, annoyed, funny, smile, elation, sarcastic"})
                    all_texts.append(input_text + show_text)
                    need_input = False
                    show_text = ""
                    input_text = ""

                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.9,
                        max_tokens=100
                    )
                else:
                    messages.append(
                        {"role": "user",
                         "content": content + f"//Asuka sees: {set(detected_objects)} "+ "(Stay in character, AFTER // THIS SYMBOL DESCRIBE WHAT YOU CHARACTAR DOING)"})
                    all_texts.append(input_text + show_text)
                    need_input = False
                    show_text = ""
                    input_text = ""

                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.9,
                        max_tokens=100
                    )
                chat_response = completion.choices[0].message.content
                messages.append({"role": "assistant", "content": chat_response})
                fin_chat_response = chat_response.split("//")

                all_texts.append(fin_chat_response[0])
                print(fin_chat_response[1])
                if need_sounds == True:
                    engine.say(fin_chat_response[0])
                    engine.runAndWait()

            #when a user enters a message it can be too long, so i only display part of it
            #to erase text we should delete the last symbol, and add to show text one symbol from whole text
            elif event.key == pygame.K_BACKSPACE:
                show_text = show_text[:-1]
                try:
                    show_text = input_text[-1] + show_text
                    input_text = input_text[:-1]
                except:
                    pass
            else:
                if len(show_text) > 40:
                    input_text += show_text[0]
                    show_text = show_text[1:]
                show_text += event.unicode




    if keys[pygame.K_TAB]:
        #input mod - all signals from keyboard will be letters
        need_input = True

    if text_rect.collidepoint(mouse_pos):
        #opportunity input text just by pressing button in input field
        if pygame.mouse.get_pressed()[0]:
            need_input = True

    if btts_rect.collidepoint(mouse_pos):
        # switching text to speech button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if need_sounds == False:
                need_sounds = True
                ttsbtn = pygame.image.load("ttson.png")
                btts_surf.blit(ttsbtn, (3, 3))
            elif need_sounds == True:
                need_sounds = False
                ttsbtn = pygame.image.load("ttsoff.png")
                btts_surf.blit(ttsbtn, (3, 3))


    text1 = font.render(show_text, True, (0, 0, 0))
    screen.blit(text1, (460, 500))

    num_lines = 0
    #finnaly! this code display text as in Twitch chat
    for text in reversed(all_texts):
        if text.startswith("Asuka: "):
            text_surface = font.render(text, True, red)
            text_color = red
        else:
            text_surface = font.render("Me: "+ text, True, green)
            text_color = green
            text = "Me: " + text

        # splitting text into lines of 40 characters (max counts of symbols in the line - 40)
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if font.size(current_line + word)[0] < 300:
                current_line += word + " "
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        # output each line of the text
        for line in reversed(lines):
            text_surface = font.render(line, True, text_color)
            text_width, text_height = font.size(line)
            screen.blit(text_surface, (x, y - (num_lines + 1) * line_height - text_height))
            num_lines += 1

    #this block try - except made for detecting emotion in text, and display sprite that needed
    try:
        if fin_chat_response[1].lower() in textemo or (count % 2 == 0):
            emo = fin_chat_response[1].lower()
            if count % 2 == 1:
                if emo == "sarcastic":
                    dog_rect = sarcastic_vibe.get_rect(
                        bottomright=(525, 600))
                    screen.blit(sarcastic_vibe, dog_rect)
                if emo == "neutral":
                    dog_rect = neutral_vibe.get_rect(
                        bottomright=(525, 600))
                    screen.blit(neutral_vibe, dog_rect)
                if emo == "dont understand":
                    dog_rect = unknown.get_rect(
                        bottomright=(525, 600))
                    screen.blit(unknown, dog_rect)
                if emo == "annoyed":
                    dog_rect = annoy_vibe.get_rect(
                        bottomright=(525, 600))
                    screen.blit(annoy_vibe, dog_rect)
                if emo == "funny":
                    dog_rect = laught.get_rect(
                        bottomright=(525, 600))
                    screen.blit(laught, dog_rect)
                if emo == "smile":
                    dog_rect = smile.get_rect(
                        bottomright=(525, 600))
                    screen.blit(smile, dog_rect)
                if emo == "elation":
                    dog_rect = elation.get_rect(
                        bottomright=(525, 600))
                    screen.blit(elation, dog_rect)
                    print("maintry")
            else:
                #and if switcher was on Dalle side
                # we are launching dalle
                if fin_chat_response[0] != prev_chat_response0:
                    print("creating..")
                    threading.Thread(target=load_image,
                                     args=(emo,)).start()  # start loading the image in a separate stream
                    print("Finich!")
                else:
                    image_path = "my_image.png"
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as f:
                            image_data = pygame.image.load(f)
                            image_data = resize(image_data, 400)
                            dog_rect = image_data.get_rect(
                                bottomright=(425, 600))
                            screen.blit(image_data, dog_rect)

            prev_chat_response0 = fin_chat_response[0]

    except:
        dog_rect = neutral_vibe.get_rect(
            bottomright=(525, 600))
        screen.blit(neutral_vibe, dog_rect)

    #deleting all detected objects, to avoid fantom objects
    print(set(detected_objects))
    detected_objects = []
    #updating display
    #pygame.display.flip()
    pygame.display.update()

# Done! Time to quit.
#print(messages)

#save our hustory to json file and deleting our old message
#to avoid overflows of openai
with open("session_history.json", "w") as f:
    if len(messages) > 25:
        need_delete = len(messages) - beginlen
        messages = messages[need_delete:]
    json.dump(messages, f)
    print(f"i deleted {need_delete}")

pygame.quit()


#sorry!
#i want 600 lines
#so, i just say, that it was interesting
#almost...
#yey 600 lines, cool!
