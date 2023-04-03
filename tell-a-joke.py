
# This script is meant to be run whenever the pi turns on.
# It waits for someone to push the button,
# then it visits the "official joke api" shown below and
# grabs a random joke.
# Then says the joke through a speaker connected to the audio jack.

# To make this work, we need to schedule this script.
# here are the commands to do that in terminal:
#
# sudo nano /lib/systemd/system/joke.service
# [Pi will try to open a nano text editor]
# [if you've never opened nano text editor before, you might have to choose a configuration option]
# [I chose the recommended option (option 1)]
# [in the nano editor, add this text (or something similar):]
'''
[Unit]
Description=Joke service
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /home/rodriguep/Desktop/scripts/tell-a-joke/tell-a-j>

[Install]
WantedBy=multi-user.target
'''
# We need Pi to run the python code below after the wifi connection is established,
# which is why i didn't just run this as a crob job at reboot (although maybe there's a good way to do this).
# After you've entered the text above, hit CTRL-S to save and CTRL-X to exit the nano editor.

# start python script:
import gtts   # google text to speech API. We send the text to this API and it returns an MP3 file for us to play.
import subprocess
import alsaaudio    # allows us to change the output volume
import RPi.GPIO as GPIO
import os, sys, time
from urllib.request import urlopen
import json

# configure the button you'll press to tell the Pi to go get a joke
GPIO.setmode(GPIO.BOARD)   # Tells Pi to use physical pin numberings
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # set pin 10 to be an input pin & set so initial/default is "low"/off
# configure the LED
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)

# adjust the volume
m = alsaaudio.Mixer('PCM')
m.setvolume(95)

def getJoke():
    url = 'https://official-joke-api.appspot.com/jokes/general/random'
    response = urlopen(url)
    data_json = json.loads(response.read())
    setup = data_json[0]['setup']
    punchline = data_json[0]['punchline']
    
    return (setup, punchline)

def getJokeAndSaveJoke():
    setup, punchline = getJoke()
    setup_mp3 = gtts.gTTS(text=setup, lang='en')
    setup_mp3.save('/home/rodriguep/Desktop/scripts/tell-a-joke/temp_files/setup.mp3')
    punchline_mp3 = gtts.gTTS(text=punchline, lang='en')
    punchline_mp3.save('/home/rodriguep/Desktop/scripts/tell-a-joke/temp_files/punchline.mp3')
    
def sayJoke():
    subprocess.Popen(['mpg321', '-q', '/home/rodriguep/Desktop/scripts/tell-a-joke/temp_files/setup.mp3']).wait()
    time.sleep(2)
    subprocess.Popen(['mpg321', '-q', '/home/rodriguep/Desktop/scripts/tell-a-joke/temp_files/punchline.mp3']).wait()

GPIO.output(8, GPIO.HIGH)  # turn on the LED to show the script is running
while True:
    if GPIO.input(10) == GPIO.HIGH:
        print('button was pushed!')
        
        getJokeAndSaveJoke()
        sayJoke()
        time.sleep(1)
