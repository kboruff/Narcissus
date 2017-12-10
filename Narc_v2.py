from multiprocessing import Process, Queue
import imutils
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import time
import cv2
import numpy as np
import random

#Servo Prep
ServoBlaster = open('/dev/servoblaster', 'w')		# ServoBlaster is what we use to control the servo motors

# Set ServoBlaster Limits
# Servo Pins
PanServo = 1
TiltServo = 2
# Upper Limit
_TiltServoUL = 160
_PanServoUL = 190
# Lower Limit
_TiltServoLL = 120
_PanServoLL = 150

# Set Default positions
#curPosPan = round((_PanServoUL + _PanServoLL)/2) #Uncomment to make pan and tilt reset to middle
#curPostilt = round((_TiltServoUL + _TiltServoLL)/2)
curPosPan = 190
curPosTilt = 145

#Initialize desired positions
desPosTilt = 0
desPosPan = 0

#Random variables
randMovePan = random.randint(_PanServoLL, _PanServoUL)
randMoveTilt = random.randint(_TiltServoLL, _TiltServoUL)

#Processing Queues
panCurPosQ = Queue()	# Servo Pan current position, sent by subprocess and read by main process
tiltCurPosQ = Queue()	# Servo Tilt current position, sent by subprocess and read by main process
panDesPosQ = Queue()	# Servo Pan desired position, sent by main and read by subprocess
tiltDesPosQ = Queue()	# Servo Tilt desired position, sent by main and read by subprocess
panCurSpeedQ = Queue()	# Servo Pan speed, sent by main and read by subprocess
tiltCurSpeedQ = Queue()	# Servo Tilt speed, sent by main and read by subprocess
CurFrame = Queue()

def Pan(curPosPan, desPosPan):	# Process Pan controls PanServo
	speed = .1				# Here we set some defaults:
	desPosPan = curPosPan+1		# 	we can be sure we know where the servo really is. (or will be soon)
	print("Pan Process started" + '\n')
	while True:
		time.sleep(speed)
		if panCurPosQ.empty():			# Update panCurPos in case the main process needs-
			panCurPosQ.put(curPosPan)		# to read it
		
		if not panDesPosQ.empty():		# Read panCurDesPos in case the main process-
			desPosPan = panDesPosQ.get()	#	has updated it

		if not panCurSpeedQ.empty():			# Read panCurSpeed in case the main process-
			_panCurSpeed = panCurSpeedQ.get()	# has updated it, the higher the speed value, the shorter-
			speed = .1 / _panCurSpeed			# the wait between loops will be, so the servo moves faster
		
		if curPosPan < desPosPan:					# if panCurPos less than panCurDesPos
			curPosPan += 1							# incriment panCurPos up by one
			panCurPosQ.put(curPosPan)					# move the servo that little bit
			#print("PanMove called: " + str(curPosPan) + '<' + str(desPosPan) + '\n')
			ServoBlaster.write(str(PanServo) + '=' + str(curPosPan) + '\n')	#
			ServoBlaster.flush()					#
			if not panCurPosQ.empty():				# throw away the old panCurPos value,-
				trash = panCurPosQ.get()				# it's no longer relevent

		if curPosPan > desPosPan:					# if panCurPos greater than panCurDesPos
			curPosPan -= 1						# incriment panCurPos down by one
			panCurPosQ.put(curPosPan)					# move the servo that little bit
			#print("PanMove called: " + str(curPosPan) + '>' + str(desPosPan) + '\n')
			ServoBlaster.write(str(PanServo) + '=' + str(curPosPan) + '\n')	#
			ServoBlaster.flush()					#
			if not panCurPosQ.empty():				# throw away the old panCurPos value,-
				trash = panCurPosQ.get()			# it's no longer relevent
				
		if curPosPan == desPosPan:			# if all is good,-
			_panCurSpeed = 1			# slow the speed; no need to eat CPU just waiting
			
def Tilt(curPosTilt, desPosTilt):	# Process Pan controls PanServo
	speed = .1				# Here we set some defaults:
	desPosPan = curPosPan+1		# 	we can be sure we know where the servo really is. (or will be soon)

	print("Tilt Process started" + '\n')
	while True:
		time.sleep(speed)
		if tiltCurPosQ.empty():			# Update panCurPos in case the main process needs-
			tiltCurPosQ.put(curPosTilt)		# to read it
		
		if not tiltDesPosQ.empty():		# Read panCurDesPos in case the main process-
			desPosTilt = tiltDesPosQ.get()	#	has updated it

		if not tiltCurSpeedQ.empty():			# Read panCurSpeed in case the main process-
			_tiltCurSpeed = tiltCurSpeedQ.get()	# has updated it, the higher the speed value, the shorter-
			speed = .1 / _tiltCurSpeed			# the wait between loops will be, so the servo moves faster
		
		if curPosTilt < desPosTilt:					# if panCurPos less than panCurDesPos
			curPosTilt += 1							# incriment panCurPos up by one
			tiltCurPosQ.put(curPosTilt)					# move the servo that little bit
			#print("TiltMove called: " + str(curPosTilt) + '<' + str(desPosTilt) + '\n')
			ServoBlaster.write(str(TiltServo) + '=' + str(curPosTilt) + '\n')	#
			ServoBlaster.flush()					#
			if not tiltCurPosQ.empty():				# throw away the old panCurPos value,-
				trash = tiltCurPosQ.get()				# it's no longer relevent

		if curPosTilt > desPosTilt:					# if panCurPos greater than panCurDesPos
			curPosTilt -= 1						# incriment panCurPos down by one
			tiltCurPosQ.put(curPosTilt)					# move the servo that little bit
			#print("TiltMove called: " + str(curPosTilt) + '>' + str(desPosTilt) + '\n')
			ServoBlaster.write(str(TiltServo) + '=' + str(curPosTilt) + '\n')	#
			ServoBlaster.flush()					#
			if not tiltCurPosQ.empty():				# throw away the old panCurPos value,-
				trash = tiltCurPosQ.get()				# 	it's no longer relevent
				
		if curPosTilt == desPosTilt:	        # if all is good,-
			_tiltCurSpeed = 1		        # slow the speed; no need to eat CPU just waiting

# Start processing queues
Process(target=Pan, args=(curPosPan, desPosPan)).start()	# Start the subprocesses
Process(target=Tilt, args=(curPosTilt, desPosTilt)).start()	# Start the subprocesses
#time.sleep(1)				# Wait for them to start

#Return Servo to default position
print("Setting Pan Pan to " + str(curPosPan))
print(str(PanServo) + '=' + str(curPosPan) + '\n')
print("Setting Tilt Pan to " + str(curPosTilt))
panDesPosQ.put(curPosPan)
tiltDesPosQ.put(curPosTilt)
print('Defaults set')

def PanMove(distance, speed, curPosPan, desPosPan):		# We are provided a distance positive or negative to move and a speed to move.
	if not panCurPosQ.empty():		# Read it's current position given by the subprocess(if it's avalible)-
		curPosPan = panCurPosQ.get()	# 	and set the main process global variable.
	desPosPan = curPosPan + distance	# The desired position is the current position + the distance to move.
	
	if desPosPan > _PanServoUL:		# Only move AS far as set limit.
		desPosPan = _PanServoUL
		
	if desPosPan < _PanServoLL:		# Only move AS far as set limit.
		desPosPan = _PanServoLL		
	panDesPosQ.put(desPosPan)
	panCurSpeedQ.put(speed)
	return;

def TiltMove(distance, speed, curPosTilt, desPosTilt):		# We are provided a distance positive or negative to move and a speed to move.
	if not tiltCurPosQ.empty():		# Read it's current position given by the subprocess(if it's avalible)-
		curPosTilt = tiltCurPosQ.get()	# 	and set the main process global variable.
	desPosTilt= curPosTilt + distance	# The desired position is the current position + the distance to move.

	if desPosTilt > _TiltServoUL:		# Only move AS far as set limit.
		print("TiltMove called: desired position is beyond upper limit" + '\n')
		desPosTilt = _TiltServoUL		
	if desPosTilt < _TiltServoLL:		# Only move AS far as set limit.
		print("TiltMove called: desired position is beneath lower limit" + '\n')
		desPosTilt = _TiltServoLL
	tiltDesPosQ.put(desPosTilt)
	tiltCurSpeedQ.put(speed)			# Send the new speed to the subprocess
	return;
	
#Video Prep
camWandH = np.array([320, 240]) #set camera frame height and width here
camCenter = [(camWandH[0]/2),(camWandH[1]/2)] #Ordered as Pan and Tilt
print("Center of screen is " + str(camCenter[0]) + ", " + str(camCenter[1]))
frontalface = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
profileface = cv2.CascadeClassifier("haarcascade_profileface.xml")
cv2.namedWindow('CreepyEye', cv2.WINDOW_NORMAL)
vs = WebcamVideoStream(src=0).start() #If src is changed to a URL it will use that as the camera

while True:
	# Capture frame-by-frame
	frame = vs.read()
	# Our operations on the frame come here
	frame = imutils.resize(frame, width=camWandH[0])
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	cv2.flip(gray,1,gray)	#	flip the image
	face = np.array([0,0,0,0])	# This will hold the array that OpenCV returns when it finds a face: (makes a rectangle)
	Cface = np.array([0,0])		# Center of the face: a point calculated from the above variable
	lastface = 0		# int 1-3 used to speed up detection. The script is looking for a right profile face,-
						# a left profile face, or a frontal face; rather than searching for all three every time,-
						# it uses this variable to remember which is last saw: and looks for that again. If it-
						# doesn't find it, it's set back to zero and on the next loop it will search for all three.-
						# This basically triples the detect time so long as the face hasn't moved much.

	faceFound = False	# This variable is set to true if, on THIS loop a face has already been found
						# We search for a face three diffrent ways, and if we have found one already-
						# there is no reason to keep looking.
	cv2.imshow('CreepyEye',gray)
	#Find Faces
	if not faceFound:
		if lastface == 0 or lastface == 1:
			fface = frontalface.detectMultiScale(gray, 1.3, 4, 0, (80,80))		
			if fface != ():			# if we found a frontal face...
				lastface = 1		# set lastface 1 (so next loop we will only look for a frontface)
				for f in fface:		# f in fface is an array with a rectangle representing a face
					faceFound = True
					face = f

	if not faceFound:				# if we didnt find a face yet...
		if lastface == 0 or lastface == 2:	# only attempt it if we didn't find a face last loop or if-
			pfacer = profileface.detectMultiScale(gray, 1.3, 4,0,(80,80))
			if pfacer != ():		# if we found a profile face...
				lastface = 2
				print("pfacer is " + str(pfacer))
				for f in pfacer:
					faceFound = True
					face = f

	if not faceFound:				# a final attempt
		if lastface == 0 or lastface == 3:	# flipped profile face search because the Profile is only tuned for right profiles
			grayRev = cv2.flip(gray,1)
			pfacel = profileface.detectMultiScale(grayRev, 1.3, 4,0,(80,80))
			if pfacel != ():
				lastface = 3
				print("pfacel is " + str(pfacel))
				for f in pfacel:
					faceFound = True
					face = f

	if not faceFound:		# if no face was found...-
		lastface = 0		# the next loop needs to know
		face = np.array([0,0,0,0])	# so that it doesn't think the face is still where it was last loop
		#time.sleep(random.uniform(.001,2.999))

	if faceFound == True:
		x,y,w,h = face
		Cface = [(face[2]/2+face[0]),(face[3]/2+face[1])]	# we are given an x,y corner point and a width and height, we need the center
		centerPan = "middle "	
		centerTilt = ""
		print("Center of face is " + str(Cface[0]) + ", " + str(Cface[1]))
		if lastface == 1:
			#Draw a rectangle around every found face
			cv2.rectangle(gray,(x,y),(x+w,y+h),(255,255,255),1)
			cv2.putText(gray, "Frontal Face Detected", (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1, cv2.LINE_AA)
			cv2.circle(gray, (int(Cface[0]), int(Cface[1])), 1, 255, 2)
			cv2.putText(gray, "Center", (int(Cface[0]), int(Cface[1])), cv2.FONT_HERSHEY_SIMPLEX, .3, (255,255,255), 1, cv2.LINE_AA)
		elif lastface == 2:
			#Draw a rectangle around every found face
			cv2.rectangle(gray,(x,y),(x+w,y+h),(255,255,255),1)
			cv2.putText(gray, "Right Profile Detected", (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1, cv2.LINE_AA)
			cv2.circle(gray, (int(Cface[0]), int(Cface[1])), 1, 255, 2)
			cv2.putText(gray, "Center", (int(Cface[0]), int(Cface[1])), cv2.FONT_HERSHEY_SIMPLEX, .3, (255,255,255), 1, cv2.LINE_AA)
		elif lastface == 3:
			#Draw a rectangle around every found face
			cv2.rectangle(grayRev,(x,y),(x+w,y+h),(255,255,255),1)
			cv2.putText(grayRev, "Left Profile Detected", (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1, cv2.LINE_AA)
			cv2.circle(grayRev, (int(Cface[0]), int(Cface[1])), 1, 255, 2)
			cv2.putText(grayRev, "Center", (int(Cface[0]), int(Cface[1])), cv2.FONT_HERSHEY_SIMPLEX, .3, (255,255,255), 1, cv2.LINE_AA)
			gray = cv2.flip(grayRev,1)
		
		#print("Face position is " + str((face)))
		#Draws dot in center of camera display
		cv2.circle(gray, (int(camCenter[0]), int(camCenter[1])), 1, 255, 2)
		cv2.putText(gray, "Center of Camera", (int(camCenter[0]), int(camCenter[1])),cv2.FONT_HERSHEY_SIMPLEX, .3, (255,255,255), 1, cv2.LINE_AA)

		# Display the resulting frame
		cv2.imshow('CreepyEye',gray)
		cv2.waitKey(33) #Displays image for length of a single frame in 30 FPS
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		boundFace = 3
		absoluteDistanceX = abs(Cface[1] - camCenter[1])
		absoluteDistanceY = abs(Cface[0] - camCenter[0])
		if int(Cface[0]) > (camCenter[0]) and absoluteDistanceX > boundFace:
			distance =0
			speed =.1
			if absoluteDistanceX > 40:
				distance = 7
				speed = 1
			elif absoluteDistanceX > 20:
				distance = 4
				speed = .5
			elif absoluteDistanceX > 5:
				distance = 1
				speed = .1
			print(str(PanServo) + '=' + str(curPosPan) + '\n')
			PanMove(distance,speed,curPosPan, desPosPan)			
			centerPan = "right "
		
		elif int(Cface[0]) < (camCenter[0]) and absoluteDistanceX > boundFace:
			distance =0
			speed =.1
			if absoluteDistanceX > 40:
				distance = 7
				speed = 1
			elif absoluteDistanceX > 20:
				distance = 4
				speed = .5
			elif absoluteDistanceX > 8:
				distance = 1
				speed = .1
			centerPan = "left "
			PanMove((distance*-1),speed,curPosPan, desPosPan)
			print(str(PanServo) + '=' + str(curPosPan) + '\n')
			
		
		if int(Cface[1]) > (camCenter[1]) and absoluteDistanceY > boundFace:
			distance =0
			speed =.1
			if absoluteDistanceY > 20:
				distance = 9
				speed = 1
			elif absoluteDistanceY > 10:
				distance = 4
				speed = .5
			elif absoluteDistanceY > 5:
				distance = 1
				speed = .1
			print(str(PanServo) + '=' + str(curPosPan) + '\n')
			TiltMove(distance,speed,curPosTilt, desPosTilt)
			centerTilt = "lower "		
		elif int(Cface[1]) < (camCenter[1]) and absoluteDistanceY > boundFace:
			distance =0
			speed =.1
			if absoluteDistanceY > 20:
				distance = 9
				speed = 1
			elif absoluteDistanceY > 10:
				distance = 4
				speed = .5
			elif absoluteDistanceY > 5:
				distance = 1
				speed = .1
			print(str(PanServo) + '=' + str(curPosPan) + '\n')
			TiltMove((distance*-1),speed,curPosTilt, desPosTilt)
			centerTilt = "upper "
		
		if absoluteDistanceY <= boundFace and absoluteDistanceX <= boundFace:
			cv2.putText(gray, "Face found!", (10,220), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1, cv2.LINE_AA)
			pass
		#cv2.putText(gray, "Face is " + centerTilt + centerPan + " of camera center", (10,220), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1, cv2.LINE_AA)
	
	if not faceFound:		# if no face was found...-
		print("Entering search mode")
		PanMove(random.randint(-200,200),random.randint(1,3),curPosPan, desPosPan)
		randMovePan = random.randint(_TiltServoLL, _TiltServoUL)
		TiltMove(random.randint(-200,200),random.randint(1,3),curPosTilt, desPosTilt)
		randMoveTilt = random.randint(_PanServoLL, _PanServoUL)
		print("randMoveTilt " + str(randMoveTilt) + " curPosTilt " + str(curPosTilt) + " randMovePan " + str(randMovePan) + " curPosPan " + str(curPosPan))
		cv2.putText(gray, "Searching Mode Active", (10,220), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1, cv2.LINE_AA)
		cv2.imshow('CreepyEye',gray)
		cv2.waitKey(33) #Displays image for length of a single frame in 30 FPS
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

# When everything done, release the capture
#vs.release()
cv2.destroyAllWindows()