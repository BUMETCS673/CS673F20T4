#-------------------------------------#
#       Call camera to detect
#-------------------------------------#
from retinaface import Retinaface
from PIL import Image
import numpy as np
import cv2
import time
retinaface = Retinaface()
# call the camera
capture=cv2.VideoCapture(0) # capture=cv2.VideoCapture("1.mp4")

fps = 0.0
while(True):
    t1 = time.time()
    # read a frame
    ref,frame=capture.read()
    # transform BGR to RGB
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    # detect
    frame = np.array(retinaface.detect_image(frame))

    # RGB to BGR for meeting opencv display format
    frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)

    fps  = ( fps + (1./(time.time()-t1)) ) / 2
    print("fps= %.2f"%(fps))
    frame = cv2.putText(frame, "fps= %.2f"%(fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("video",frame)

    c = cv2.waitKey(1) & 0xff
    if c == 27:
        capture.release()
        break
