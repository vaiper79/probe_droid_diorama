# Python3

# Version 6, 25.11.2019, OleA aka vaiper79
# Volume configuration by Adafruit:
# Hardware: MCP3008 DAC Chip 
# Code: https://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/overview
# Amplifier configuration by Adafruit:
# Hardware: TPA2016 i2c amplifier
# Code: https://learn.adafruit.com/adafruit-tpa2016-2-8w-agc-stereo-audio-amplifier/python-circuitpython
# Logging Code: https://gist.github.com/sweenzor/1782457
# Shutdown: https://gpiozero.readthedocs.io/en/stable/recipes.html#shutdown-button

import pygame, random, time, os, busio, digitalio, board, adafruit_tpa2016, logging, logging.handlers
from gpiozero import Button, PWMLED, LED
from subprocess import check_call
from signal import pause

## Some variables
# Shutdown
shDwn = False
# Audio
volume = 0.6
started = 0
rndmChatterMillis = 0
lastChatterMillis = 0
rndmTelemetryMillis = 0
lastTelemetryMillis = 0
musicTriggered = 0
musicState = 0
# LEDs
lastLEDMillis = 0
lastCountDMillis = 0
LEDMillis = 60
brList = [0.001, 0.02, 0.005, 0.01, 0.008, 0.012, 0.015, 0.002, 0.007, 0.017, 0.011, 0.009] # Brightnesses to use for flickering lights
shDwnBr = 0.1

# Set up logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
formatter = logging.Formatter('%(module)s.%(funcName)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

# Amplifier code
i2c = busio.I2C(board.SCL, board.SDA)
tpa = adafruit_tpa2016.TPA2016(i2c)
tpa.fixed_gain = 0 # Anything above and the way it is connected now causes clipping. Perhaps separate of more powerful PSU = more oomf!

# GPIO Pins defined
button_top = Button(17, hold_time=3)  
button_volUp = Button(4)
button_volDwn = Button(27)
led_front1 = PWMLED(5)
led_front2 = PWMLED(6)
led_front3 = PWMLED(13) 
led_front4 = PWMLED(19)
led_button = PWMLED(26)
#led_droidRed = GPIO.PWM(18, 1000) # HW PWM
led_droidRed = PWMLED(18)
led_droidYlw = PWMLED(16)

# Making sure all is dark
led_front1.value = 0
led_front2.value = 0
led_front3.value = 0
led_front4.value = 0
led_button.value = 0
led_droidRed.value = 0
led_droidYlw.value = 0

pygame.init() # Required to get_ticks() since start

bg_music = "/home/pi/droid/audio/background_music.wav"

#set up the mixer
freq = 44100     # audio CD quality
bitsize = -16    # unsigned 16 bit
channels = 2     # 1 is mono, 2 is stereo
buffer = 2048    # number of samples (experiment to get right sound)
pygame.mixer.init(freq, bitsize, channels, buffer)
pygame.mixer.set_num_channels(10) # Not to be confused with the number of channels..right..this is # of "voices"

# Load up the bg music for continous playback 
pygame.mixer.music.load(bg_music)

#Create a Channel for each type of audio track
musicChannel = pygame.mixer.Channel(1)
chatterChannel = pygame.mixer.Channel(2)
hoverChannel = pygame.mixer.Channel(3)
telemetryChannel = pygame.mixer.Channel(4)

# Set the volume for all channels separately.. 
pygame.mixer.music.set_volume(volume)
pygame.mixer.Channel(1).set_volume(volume)
pygame.mixer.Channel(2).set_volume(volume)
pygame.mixer.Channel(3).set_volume(volume)
pygame.mixer.Channel(4).set_volume(volume)

def volumeChange(volume):
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.Channel(1).set_volume(volume)
    pygame.mixer.Channel(2).set_volume(volume)
    pygame.mixer.Channel(3).set_volume(volume)
    pygame.mixer.Channel(4).set_volume(volume)

def doIt(): # Could do one thing on the first press..something else on the next..etc...but what.. 
    global musicState
    global musicTriggered
    log.debug("Turning off music")
    if (musicState == 0 and musicTriggered == 0):
        print("Set volume 0")
        pygame.mixer.music.set_volume(0)
        musicState = 1
        musicTriggered = 1
    if (musicState == 1 and musicTriggered == 0):
        pygame.mixer.music.set_volume(volume)
        musicState = 0
        musicTriggered = 1
    musicTriggered = 0

def shutDown():
    global shDwn 
    shDwn = True
    log.debug("Shutting down amplifier")
    tpa.amplifier_shutdown = True
    log.debug("Counting down..")
    led_front1.value = shDwnBr
    led_front2.value = shDwnBr
    led_front3.value = shDwnBr
    led_front4.value = shDwnBr
    time.sleep(0.5)             # It is fine, we are about to shut down, no more input or output at this time
    led_front4.value = 0
    time.sleep(0.5)
    led_front3.value = 0
    time.sleep(0.5)
    led_front2.value = 0
    time.sleep(0.5)
    led_front1.value = 0
    led_droidRed = 0
    led_droidYlw = 0
    led_button = 0
    log.debug("Shutting down droid controller")
    #check_call(['sudo', 'poweroff']) # Shutsdown the OS. Will leave this out until prod.. 
    time.sleep(10)

def volDwn():
    log.debug("Volume Down")
    global volume
    volume = volume - 0.05
    volumeChange(volume)

def volUp():
    log.debug("Volume Up")
    global volume
    volume = volume + 0.05
    volumeChange(volume)

# Start amplifier
log.debug("Switching on the amplifier")
tpa.amplifier_shutdown = False # Not strickly necessary..but for completeness. 

while True:

## BUTTONS ## - More or less done

    button_top.when_held = shutDown # Hold for 3 seconds to shut down..requires power cycle. 
    button_top.when_released = doIt
    button_volUp.when_released = volUp
    button_volDwn.when_released = volDwn

## LIGHTS ## - FAR from done.. 
    if (shDwn == False):
        if (pygame.time.get_ticks() - lastLEDMillis >= LEDMillis):
            led_front1.value = random.choice(brList)
            led_front2.value = random.choice(brList)
            led_front3.value = random.choice(brList)
            led_front4.value = random.choice(brList)
            led_droidRed.value = random.choice(brList)
            led_droidYlw.value = random.choice(brList)
            lastLEDMillis = pygame.time.get_ticks()

## MUSIC ## - More or less done

    # Background Music Playing 
    if started == 0:
        log.debug("Playing BG music indefinately")
        pygame.mixer.music.play(loops=-1)  # Looping the loaded music file indef.. 
        started = 1

    # Droid Hover, randomized in content
    if hoverChannel.get_busy() == False:
        rand = str(random.randrange(1, 8))
        log.debug("Playing hover:" + str(rand))
        hoverChannel.play(pygame.mixer.Sound("/home/pi/droid/audio/hover"+rand+".wav"))

    # Droid Chatter, randomized in content and time
    if (pygame.time.get_ticks() - lastChatterMillis >= rndmChatterMillis) and (chatterChannel.get_busy() == False) and (telemetryChannel.get_busy() == False):
        rand = str(random.randrange(1, 19))
        rndmChatterMillis = random.randrange(800, 8000)
        log.debug("Playing chatter:" + str(rand) + ", " + str(rndmChatterMillis) + " since last")
        lastChatterMillis = pygame.time.get_ticks()
        chatterChannel.play(pygame.mixer.Sound("/home/pi/droid/audio/chatter"+rand+".wav"))

    # Droid Chatter, randomized in content and time
    if (pygame.time.get_ticks() - lastChatterMillis >= rndmChatterMillis) and (chatterChannel.get_busy() == False) and (telemetryChannel.get_busy() == False):
        rand = str(random.randrange(1, 8))
        rndmTelemetryMillis = random.randrange(1000, 15000)
        log.debug("Playing telemetry:" + str(rand) + ", " + str(rndmTelemetryMillis) + " since last")
        lastTelemetryMillis = pygame.time.get_ticks()
        telemetryChannel.play(pygame.mixer.Sound("/home/pi/droid/audio/telemetry"+rand+".wav"))