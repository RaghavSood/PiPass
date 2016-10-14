import RPi.GPIO as GPIO
import time
import math
 
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
 
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
GPIO.setmode(GPIO.BCM)

GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin()
 
# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

padding = 2
shape_width = 20
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = padding
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(font='font.ttf',size=9,index=0,encoding='unic')
topline = ""
bottomline = ["", "", "", ""]

folders = ["Email", "Bank", "Social", "Device", "Accounts", "Misc"]

def drawtext(i):
	global image
        global draw
        global font
	global topline
	global bottomline
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((x, top), topline,  font=font, fill=255)
	draw.text((x, top+15), bottomline[0], font=font, fill=255)
	draw.text((x, top+25), bottomline[1], font=font, fill=255)
	draw.text((x, top+35), bottomline[2], font=font, fill=255)
	draw.text((x, top+45), bottomline[3], font=font, fill=255)
        if i is True:
                image = image.convert('L')
                image = ImageOps.invert(image)
                image = image.convert('1')
        # Display image.
        disp.image(image)
        disp.display()

def toptext(s, i):
        global topline
        topline = s
        drawtext(i)

def bottomtext(s, i):
        global bottomline
        bottomline = s
        drawtext(i)

def by2(s):
	out = []
	if s == "abcdefghijklmnopqrstuvwxyz0123456789@.":
		out = ["abcdefghijklmnopqrstuvwxyz", "1234567890@."]
		return out
	size = int(math.ceil(len(s)/2.0) * -1)
	print size
	while len(s):
		out.insert(0, s[size:])
		s = s[:size]
	return out

def input():
	keyboard = "abcdefghijklmnopqrstuvwxyz0123456789@."
	word = ""
	oldtopline = topline
	while True:
		print "Word:", word
		toptext(word, False)
		numOpts = len(keyboard)
		print str(numOpts) + " options"
		options = by2(keyboard)
		print options
		if len(keyboard) == 1:
			word = word + keyboard
			keyboard = "abcdefghijklmnopqrstuvwxyz0123456789@."
			continue
		else:
			bottomtext(["Use the buttons", "to choose groups", options[0], options[1]], False)
			option = click()
			if option == 2:
				toptext(oldtopline, False)
				return word
			if option ==3:
				toptext(oldtopline, False)
				return "Cancelled"
			keyboard = options[int(option)]

def click():
	while True:
		input_select = GPIO.input(12)
		if input_select == False:
			return 2
		input_up = GPIO.input(20)
		if input_up == False:
			return 1
		input_down = GPIO.input(21)
		if input_down == False:
			return 0
		input_back = GPIO.input(26)	
		if input_back == False:
			return 3

def lock():
	global topline
	topline = "LOCKED"
	global bottomline
	bottomline = [" ", " ", "    _  _  _  _  _  _  ", " "]
	drawtext(False)
	print "Locked"
	passcode = "021302" # DOWN SELECT UP BACK DOWN SELECT
	entered = ""
	failcount = 0
	while True:
		inputopt = click()
		entered = entered + str(inputopt)
		disptext = "    _  _  _  _  _  _  "
		disptext = disptext.replace('_', '*', len(entered))
		bottomline = [" ", " ", disptext, " "]
		drawtext(False)
		if len(entered) == 6:
			if entered == passcode:
				main()
			else:
				failcount = failcount + 1
				bottomline = [" ", " ", "       INCORRECT  ", " "]
				drawtext(False)
				time.sleep(2)
				if failcount >= 3:
					for timectr in range(0,30):
						if timectr == 29:
							bottomline = ["        Try Again", "            In ", "        "+ str(30 - timectr) + " second", " "]
						else:
							bottomline = ["        Try Again", "            In ", "       " + str(30 - timectr) + " seconds", " "]
						drawtext(False)
						time.sleep(1)
				bottomline = [" ", " ", "    _  _  _  _  _  _  ", " "]
				drawtext(False)
				entered = ""
	print "Looped"

def highlightIndex(i):
	bottomline[0] = bottomline[0].lower()
	bottomline[1] = bottomline[1].lower()
	bottomline[2] = bottomline[2].lower()
	bottomline[3] = bottomline[3].lower()
	bottomline[i] = bottomline[i].upper()
	drawtext(False)

def highlightList(i, l):
	global bottomline
	listsize = len(l)
	if int(i) <= 1:
		bottomline = [l[0], l[1], l[2], l[3]]
		highlightIndex(i)
	elif int(i) >= (listsize-2):
		bottomline = [l[listsize-4], l[listsize-3], l[listsize-2], l[listsize-1]]
		if int(i) == listsize - 1:
			highlightIndex(3)
		else:
			highlightIndex(2)
	else:
		bottomline = [l[i-1], l[i], l[i+1], l[i+2]]
		highlightIndex(1)

def foldernav(n):
	global folders
	global bottomline
	optindex = 0
	toptext("Folders", False)
	highlightList(optindex, folders)
	while True:
                inputopt = click()
                if inputopt == 2:
                        if n == 0:
				list(optindex)
			elif n == 1:
				generateIn(optindex)
                if inputopt == 1:
                        optindex = optindex + 1
                        if optindex >= len(folders):
                                optindex = len(folders) - 1
                        highlightList(optindex, folders)
                if inputopt == 0:
                        optindex = optindex - 1
                        if optindex < 0:
                                optindex = 0
                        highlightList(optindex, folders)
                if inputopt == 3:
                        main() 

def main():
	toptext("Main Menu", False)
	options = ["Retrieve", "Search", "Generate", "Lock"]
	bottomtext(options, False)
	optindex = 0
	while True:
		highlightIndex(optindex)
		inputopt = click()
		if inputopt == 2:
			if optindex == 0:
				foldernav(0)
			if optindex == 2:
				foldernav(2)
			if optindex == 3:
				lock()
		if inputopt == 1:
			optindex = optindex + 1
			if optindex >= len(options):
				optindex = len(options) - 1
			highlightIndex(optindex)
		if inputopt == 0:
			optindex = optindex - 1
                        if optindex < 0:
                                optindex = 0
			highlightIndex(optindex)
		if inputopt == 3:
			lock()

main()
