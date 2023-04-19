import cv2
import mysql.connector
import HandTracker
import RotateHandGesture
import SliderGesture
import ResizeFrameGesture


cam_width, cam_height = 1280, 720
capture = cv2.VideoCapture(0)
capture.set(3, cam_width)
capture.set(4, cam_height)
ht = HandTracker.HandRecognition()
RotateHand = RotateHandGesture.RotateHandGesture()
Slider = SliderGesture.SliderGesture()
ResizeFrame = ResizeFrameGesture.ResizeFrameGesture()

while True:
    success, img = capture.read()
    img = cv2.flip(img, 1)
    img = ht.track_hand(img)
    cv2.imshow("Camera", img)
    cv2.waitKey(1)

    hands_list = ht.get_hands()
    hand_count = ht.count_hands()
    if len(hands_list) > 0:
        # detect one-handed gestures
        for hand in hands_list:
            lm_list = hand.lm_list
            if RotateHand.detect(lm_list):
                RotateHand.execute(capture, lm_list, hands_list.index(hand))
            if Slider.detect(lm_list):
                Slider.execute(capture, lm_list, hands_list.index(hand))
        # detect multi-handed gestures
        # if len(hands_list) > 1:
        #     for hand1 in hands_list:
        #         for hand2 in hands_list:
        #             if ResizeFrame.detect(hand1, hand2):
        #                 ResizeFrame.execute(capture, hand1, hand2, hand_count)
