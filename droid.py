# Python3

# Version 4, 14.08.2019, OleA aka vaiper79
# Volume configuration by Adafruit:
# Hardware: MCP3008 DAC Chip 
# Code: https://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/overview
# Amplifier configuration by Adafruit:
# Hardware: TPA2016 i2c amplifier
# Code: https://learn.adafruit.com/adafruit-tpa2016-2-8w-agc-stereo-audio-amplifier/python-circuitpython

import pygame, random, time, os, busio, digitalio, board, adafruit_tpa2016
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from gpiozero import Button, PWMLED

# Amplifier code
i2c = busio.I2C(board.SCL, board.SDA)
tpa = adafruit_tpa2016.TPA2016(i2c)
tpa.fixed_gain = 0 # Anything above and the way it is connected now causes clipping. Perhaps separate of more powerful PSU = more oomf!

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D22)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)

# Pins defined
button = Button(17, hold_time=3)    
led1 = PWMLED(5)
led2 = PWMLED(6)
led3 = PWMLED(13)
led4 = PWMLED(19)
led5 = PWMLED(26)

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
pygame.mixer.Channel(1).set_volume(0.6)
pygame.mixer.Channel(2).set_volume(0.6)
pygame.mixer.Channel(3).set_volume(0.6)
pygame.mixer.Channel(4).set_volume(0.6)

# Some variables
debug = False
volume = 0.6
started = 0
rndmChatterMillis = 0
lastChatterMillis = 0
rndmTelemetryMillis = 0
lastTelemetryMillis = 0
blinkMillis = 50
lastBlinkMillis = 0
brightness=0
fadeAmount=0.03
last_read = 0       # this keeps track of the last potentiometer value
tolerance = 300     # to keep from being jittery we'll only change
                    # volume when the pot has moved a significant amount
                    # on a 16-bit ADC

def doIt(): # Example...
    print ("Just Do It!!!")

def remap_range(value, left_min, left_max, right_min, right_max):
    # this remaps a value from original (left) range to new (right) range
    # Figure out how 'wide' each range is
    left_span = left_max - left_min
    right_span = right_max - right_min

    # Convert the left range into a 0-1 range (int)
    valueScaled = int(value - left_min) / int(left_span)

    # Convert the 0-1 range into a value in the right range.
    return int(right_min + (valueScaled * right_span))

while True:

    if (pygame.time.get_ticks() - lastBlinkMillis >= blinkMillis):
        brightness = brightness+fadeAmount
        brightness = round(brightness, 3) # Raspberry and Python doing simple 0.1+0.1 very quickly did not work out well..

        if brightness > 1:
            brightness = 1
        if brightness <0:
            brightness = 0

        if (brightness <= 0) or (brightness >= 1): # Fade in/Fade out
            fadeAmount = -fadeAmount;

        if debug == True: print (brightness)

        # Quick and dirty pulsing of LEDs..not final product. 
        led1.value = brightness
        led2.value = brightness
        led3.value = brightness
        led4.value = brightness
        led5.value = brightness

        lastBlinkMillis = pygame.time.get_ticks()
            
    # we'll assume that the pot didn't move
    trim_pot_changed = False

    # read the analog pin
    trim_pot = chan0.value

    # how much has it changed since the last read?
    pot_adjust = abs(trim_pot - last_read)

    if pot_adjust > tolerance:
        trim_pot_changed = True

    if trim_pot_changed:
        # convert 16bit adc0 (0-65535) trim pot read into 0-100 volume level
        set_volume = remap_range(trim_pot, 0, 65535, 0, 100)

        # set OS volume playback volume
        if debug == True: print('Volume = {volume}%' .format(volume = set_volume))
        set_vol_cmd = 'sudo amixer cset numid=1 -- {volume}% > /dev/null' \
        .format(volume = set_volume)
        os.system(set_vol_cmd)

        # save the potentiometer reading for the next loop
        last_read = trim_pot

    if button.is_held:  # Used to exit when held for hold time, which now is 3 seconds
        exit()

    button.when_released = doIt

    # Background Music Playing 
    if started == 0:
        if debug == True: print ("Playing BG music indefinately")
        pygame.mixer.music.play(loops=-1)  # Looping the loaded music file indef.. 
        started = 1

    # Droid Hover, randomized in content
    if hoverChannel.get_busy() == False:
        rand = str(random.randrange(1, 8))
        if debug == True: print ("Playing hover:" + str(rand))
        hoverChannel.play(pygame.mixer.Sound("/home/pi/droid/audio/hover"+rand+".wav"))

    # Droid Chatter, randomized in content and time
    if (pygame.time.get_ticks() - lastChatterMillis >= rndmChatterMillis) and (chatterChannel.get_busy() == False) and (telemetryChannel.get_busy() == False):
        rand = str(random.randrange(1, 19))
        rndmChatterMillis = random.randrange(800, 8000)
        if debug == True: print ("Playing chatter:" + str(rand) + ", " + str(rndmChatterMillis) + " since last")
        lastChatterMillis = pygame.time.get_ticks()
        chatterChannel.play(pygame.mixer.Sound("/home/pi/droid/audio/chatter"+rand+".wav"))

    # Droid Chatter, randomized in content and time
    if (pygame.time.get_ticks() - lastChatterMillis >= rndmChatterMillis) and (chatterChannel.get_busy() == False) and (telemetryChannel.get_busy() == False):
        rand = str(random.randrange(1, 8))
        rndmTelemetryMillis = random.randrange(1000, 15000)
        if debug == True: print ("Playing telemetry:" + str(rand) + ", " + str(rndmTelemetryMillis) + " since last")
        lastTelemetryMillis = pygame.time.get_ticks()
        telemetryChannel.play(pygame.mixer.Sound("/home/pi/droid/audio/telemetry"+rand+".wav"))