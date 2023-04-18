import cv2
import mysql.connector
import HandTracker
import RotateHandGesture
import SliderGesture
import ExpandFrameGesture


cam_width, cam_height = 1280, 720
capture = cv2.VideoCapture(0)
capture.set(3, cam_width)
capture.set(4, cam_height)
ht = HandTracker.HandRecognition()
RotateHand = RotateHandGesture.RotateHandGesture()
Slider = SliderGesture.SliderGesture()
ExpandFrame = ExpandFrameGesture.ExpandFrameGesture()

while True:
    success, img = capture.read()
    # img = cv2.flip(img, 1)
    img = ht.track_hand(img)
    cv2.imshow("Camera", img)
    cv2.waitKey(1)

    hands = ht.get_landmarks_positions(img)
    for lmList in hands:
        if RotateHand.detect(lmList):
            RotateHand.execute(capture, lmList, hands.index(lmList))
        if Slider.detect(lmList):
            Slider.execute(capture, lmList, hands.index(lmList))
