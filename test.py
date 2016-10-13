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
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

GPIO.setmode(GPIO.BCM)

GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
			keyboard = options[int(option)]

def click():
	while True:
		input_select = GPIO.input(12)
		if input_select == False:
			return 2
			#time.sleep(0.2)
		input_up = GPIO.input(20)
		if input_up == False:
			return 1
			#time.sleep(0.2)
		input_down = GPIO.input(21)
		if input_down == False:
			return 0
			#time.sleep(0.2)	
def main():
	toptext("Main Menu", False)
	bottomtext(["Select:", "None", "Input", "None"], False)
	while True:
		inputopt = click()
		if inputopt == 2:
			textin = input()
			bottomtext(["Select:", "None", "Input", textin], False)
		if inputopt == 1:
			bottomtext(["Buttons:", "UP", "Select", "Down"], False)
		if inputopt == 0:
			bottomtext(["Buttons:", "Up", "Select", "DOWN"], False)

#toptext("test", False)
#time.sleep(2)
#toptext("TEST123", False)
#time.sleep(2)
#bottomtext(["Line 1", "Line 2", "", "Line 4"], True)
main()
