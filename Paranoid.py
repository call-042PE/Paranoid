import win32gui
import mss
import PIL.ImageGrab
import PIL.Image
from interception import  *
import configparser

#convert valorantsens to paladins (valorantsens / 0.819) * 6.258
#check config
config = configparser.ConfigParser()
config.read("config.ini")
sensitivity = float(config.get("config","sensitivity"))
sensitivity = int((sensitivity / 0.819) * 6.258)

S_HEIGHT = 1920
S_WIDTH = 1080

CENTER_X = 959
CENTER_Y = 539
offset_X = 2
bLeftButton = False

hWnd = win32gui.FindWindow(None,"VALORANT  ")

class Found(Exception):
	pass

def grab(x,y,w,h):
	with mss.mss() as sct:
		box = (x, y, w, h)
		img = sct.grab(box)
		return PIL.Image.frombytes('RGB',img.size,img.bgra,'raw','BGRX')

def approx(r,g,b):
	if(r >= 210 and g >= 110 and b >= 250 and r <= 255 and g <= 150 and b <= 255):
		return True
	else:
		return False

def aimassist():
	c = interception()
	c.set_filter(interception.is_mouse,interception_mouse_state.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN.value | interception_mouse_state.INTERCEPTION_MOUSE_LEFT_BUTTON_UP.value)
	while True:
		device = c.wait()
		stroke = c.receive(device)
		if(stroke.state == interception_mouse_state.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN.value):
			bLeftButton = True
		while(bLeftButton):
			img = grab(886,474,1031,608)
			try:
				for x in range(0,(1031-886)):
					for y in range(0,(608-474)):
						r,g,b = img.getpixel((x,y))
						if approx(r,g,b) and x != 0 and y != 0:
							newX = (886 + x) - CENTER_X # distance between crosshair and ennemy
							raise Found
			except Found:
				if type(stroke) is mouse_stroke:
					if(newX >= 50):
						stroke.x = abs(int(((newX - 5) / sensitivity) * offset_X))
					elif(newX <= 49):
						stroke.x = int(((newX + 5) / sensitivity) * offset_X)
					c.send(device,stroke)
			device2 = c.wait2(0)
			if device2 != 0 and interception.is_mouse(device2):
				stroke2 = c.receive(device2)
				if(stroke2.state == 2):
					stroke.state = interception_mouse_state.INTERCEPTION_MOUSE_LEFT_BUTTON_UP.value
					c.send(device,stroke)
					c.send(device2,stroke2)
					break
			c.send(device,stroke)

print(f"Offset X: {offset_X}")
aimassist()