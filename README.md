# Probe Droid Diorama

These are the files used to control the audio/lighting circuit I will use on my Imperial Probe Droid diorama. Check out my homepage/blog for more details. 

## Setting up python script to launch on RPi boot
To execute on boot;  systemd

### Step 1 – Create A Unit File
Enter the following:
```sudo nano /lib/systemd/system/droid.service```

Add in the following text :
```
[Unit]
Description=My Sample Service
 
[Service]
User=pi
WorkingDirectory=/home/pi/droid/
Type=simple
ExecStart=/usr/bin/python3 /home/pi/droid.py > /home/pi/logs/droid.log 2>&1
 
[Install]
WantedBy=multi-user.target
```
Obviously your folders may vary, and also I made sure to create the logs directory and log file. 

The permission on the unit file needs to be set to 644 :
```
sudo chmod 644 /lib/systemd/system/droid.service
```

### Step 2 – Configure systemd
Now the unit file has been defined we can tell systemd to start it during the boot sequence :
```
sudo systemctl daemon-reload
sudo systemctl enable droid.service
```

Reboot the Pi and your custom service should run:
```
sudo reboot
```

Working with services in linux:
```
sudo service droid status
sudo service droid stop
sudo service droid start
sudo service droid restart
```

## Disclaimer: 
I am NOT a professional programmer. There WILL be bugs and weird mistakes. I try to remove them when I find them, but I cannot guarantee that all my solutions used in the code are good/best practice. Also, I am pretty sure this won't destroy your hardware if you try it for yourself, but obviously I take no responsibility if you decide to use my code.. 

You have been warned :) 

Also, feel free to copy/modify and use this piece of code if you find it useful. As thanks you could always follow my blog (https://oleandre.net) and/or Instagram (https://www.instagram.com/oleshobbyblog/) and/or YouTube (https://www.youtube.com/user/vaipernor). 

/Ole