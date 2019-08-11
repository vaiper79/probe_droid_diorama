import pygame, random, time, os
from gpiozero import Button

# Pins defined
button = Button(16, hold_time=3)    
volumeUp = Button(17)                      # Rotary encoder pin A connected to GPIO2
volumeDown = Button(18)                      # Rotary encoder pin B connected to GPIO3

pygame.init() # Required to get_ticks() since start

# Make sure the system volume is where we expect
os.system("amixer sset 'PCM' 70%")

if __name__ == "__main__":
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
    pygame.mixer.Channel(0).set_volume(0.6)
    pygame.mixer.Channel(1).set_volume(0.6)
    pygame.mixer.Channel(2).set_volume(0.6)
    pygame.mixer.Channel(3).set_volume(0.6)

    # Some variables
    change = 0
    volume = 0.6
    started = 0
    rndmChatterMillis = 0
    lastChatterMillis = 0
    rndmTelemetryMillis = 0
    lastTelemetryMillis = 0

    def doIt(): # Example...
        print ("Just Do It!!!")
        #exit()

    def volume_down():                    # Pin A event handler
        print ("Volume Down")
        #pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()-0.1)
        pygame.mixer.Channel(0).set_volume(pygame.mixer.Channel(0).get_volume()-0.1)
        pygame.mixer.Channel(1).set_volume(pygame.mixer.Channel(1).get_volume()-0.1)
        pygame.mixer.Channel(2).set_volume(pygame.mixer.Channel(2).get_volume()-0.1)
        pygame.mixer.Channel(3).set_volume(pygame.mixer.Channel(3).get_volume()-0.1)
        
    def volume_up():                  
        print ("Volume Up")
        #pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()+0.1)
        pygame.mixer.Channel(0).set_volume(pygame.mixer.Channel(0).get_volume()+0.1)
        pygame.mixer.Channel(1).set_volume(pygame.mixer.Channel(1).get_volume()+0.1)
        pygame.mixer.Channel(2).set_volume(pygame.mixer.Channel(2).get_volume()+0.1)
        pygame.mixer.Channel(3).set_volume(pygame.mixer.Channel(3).get_volume()+0.1)

    while True:

        if volume >= 1:
            volume = 1
        elif volume <= 0:
            volume = 0

        button.when_released = doIt # Do stuff as it is being released..next action etc..
        volumeDown.when_released = volume_down
        volumeUp.when_released = volume_up

        if button.is_held:  # Used to exit when held for hold time, which now is 3 seconds
            exit()

        # Background Music Playing 
        if started == 0:
            print ("Playing BG music indefinately")
            pygame.mixer.music.play(loops=-1)  # Looping the loaded music file indef...
            started = 1

        # Droid Hover, randomized in content
        if hoverChannel.get_busy() == False:
            rand = str(random.randrange(1, 8))
            print ("Playing hover:" + str(rand))
            hoverChannel.play(pygame.mixer.Sound("/home/pi/droid/audio/hover"+rand+".wav"))

        # Droid Chatter, randomized in content and time
        if (pygame.time.get_ticks() - lastChatterMillis >= rndmChatterMillis) and (chatterChannel.get_busy() == False) and (telemetryChannel.get_busy() == False):
            rand = str(random.randrange(1, 19))
            rndmChatterMillis = random.randrange(800, 8000)
            print ("Playing chatter:" + str(rand) + ", " + str(rndmChatterMillis) + " since last")
            lastChatterMillis = pygame.time.get_ticks()
            chatterChannel.play(pygame.mixer.Sound("/home/pi/droid/audio/chatter"+rand+".wav"))

        # Droid Chatter, randomized in content and time
        if (pygame.time.get_ticks() - lastChatterMillis >= rndmChatterMillis) and (chatterChannel.get_busy() == False) and (telemetryChannel.get_busy() == False):
            rand = str(random.randrange(1, 8))
            rndmTelemetryMillis = random.randrange(1000, 15000)
            print ("Playing telemetry:" + str(rand) + ", " + str(rndmTelemetryMillis) + " since last")
            lastTelemetryMillis = pygame.time.get_ticks()
            telemetryChannel.play(pygame.mixer.Sound("/home/pi/droid/audio/telemetry"+rand+".wav"))