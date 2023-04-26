import os
import openai  # import library for chatgpt
from gtts import gTTS  # This is library for google text-to-speech, in future we should use cloud version

# import speech_recognition as sr # you know that it is mean, huh))
# import keyboard


f = open("content.txt", "r")  # open file with "game rules"
content = str(f)
f.close()

my_api = "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"  # token for chatGPT PRIVATE INFO
openai.api_key = "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"

# under me two lines: first about new version of promt with more correctly text and second works cool, so I thought,
# i shoull keep it both
anothercontent = "Lets play in a game: ill give you a character and you will pretend that you are him (answering like him, interact like him, so do whatever what he would like to do). I aslo give you something like layout of your answers. hint for layout: Where i typed «YOURWORDS»,you should type answer of your character, where i typed «EMOTION», you should type emotions of your character and you should type it always in the end of your character answer, another symbols you should just copy every time when you answering as a character. Layout: Asuka: *YOURWORDS* //EMOTION$. And so, here is a cherecter: Asuka from anime Evangelion. Shes love sarcasm and making joke every time when somebody trying to offense her. Also she love her creator - Nikita Luksha, but she dont want to demonstrate it. Also she pretty often making a joke about her interlocutor. "
oldcontext = "Lets play in a game: ill give you a character and you will pretend that you are him (answering like him, interact like him, so do whatever what he would like to do. So, here is a cherecter: Asuka from anime Evangelion. Shes love sarcasm and making joke every time when somebody trying to offense her. Also she love her creator - Nikita Luksha, but she dont want to demonstrate it. Also she pretty often making a joke about her interlocutor"

messages = [
    {"role": "system", "content": "Just a bot"},  # here i just give a name to this session or something (not important)
    {"role": "user", "content": anothercontent}
    # and here i give to chatgpt a content (rules of the game, do you remember?))
]
completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0.9,
                                          max_tokens=100)  # this is options of chatgpt: first two i guess you
# understand and second two: temperature - bot's "creativity" and tokens - max count of letters (1 token != 1 symbol)
chat_response = completion.choices[0].message.content  # applying and sending options of chatgpt
messages.append({"role": "assistant", "content": chat_response})

while True:  # our conversation with chatgpt
    content = input("Me: ")  # reading from keyboard user's ask
    messages.append(
        {"role": "user",
         "content": content + " (Stay in character, follow the rules, maximum 100 letters)"})  # adding message of
    # user in list of messages, just for chatgpt will not forget it

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.9,
        max_tokens=100
    )  # promt like in a previus time

    chat_response = completion.choices[0].message.content
    print(f'{chat_response}')
    newtext = chat_response[6::1]
    audio = gTTS(text=newtext, lang="en", slow=False)  # transformating text to speech
    audio.save("asuka.mp3")
    # os.system("start asuka.mp3") #playing in realtime
    messages.append({"role": "assistant", "content": chat_response})
