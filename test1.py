import cv2

import mediapipe as mp
import math
import time


class HandRecognition():
    def __init__(self, mode=False, max_hands=2, complexity=1, detection_confidence=0.6, tracking_confidence=0.6):
        self.results = None

        self.mode = mode
        self.maxHands = max_hands
        self.complexity = complexity
        self.detectionConf = detection_confidence
        self.trackingConf = tracking_confidence

        self.mpHands = mp.solutions.hands
        self.recognized_hands = self.mpHands.Hands(self.mode, self.maxHands, self.complexity,
                                                   self.detectionConf, self.trackingConf)
        self.mpDraw = mp.solutions.drawing_utils

    def track_hand(self, img, draw=True, cirRad=5, cirBGR=(255, 127, 0)):
        # convert camera feed to RGB and identify hand
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.recognized_hands.process(imgRGB)

        # visualize multiple hand
        if self.results.multi_hand_landmarks:
            for handNum in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handNum, self.mpHands.HAND_CONNECTIONS)

                    # identifies landmarks on each hand
                    for lmID, lm in enumerate(handNum.landmark):
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)

                        # highlight root of palm, tip of thumb, tip of index, tip of middle, tip of ring, tip of pinky
                        if (lmID == 0) or (lmID == 4) or (lmID == 8) or (lmID == 12) or (lmID == 16) or (lmID == 20):
                            cv2.circle(img, (cx, cy), cirRad, cirBGR, cv2.FILLED)
        return img

    def get_landmarks_positions(self, img, handNum=0):
        lmList = []

        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[handNum]
            for lmID, lm in enumerate(hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([lmID, cx, cy])
            return lmList

        # if landmark list is empty, return all IDs as 0
        for lmID in range(20):
            lmList.append([lmID, 0, 0])
        return lmList


def test_ratio(img, lmList):
    x1, y1 = lmList[4][1], lmList[4][2]
    x2, y2 = lmList[8][1], lmList[8][2]
    x3, y3 = lmList[12][1], lmList[12][2]
    # cv2.line(img, (x1, y1), (x2, y2), (255, 127, 0), 3)
    # cv2.line(img, (x2, y2), (x3, y3), (255, 127, 0), 3)
    len1 = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
    len2 = math.sqrt(math.pow(x2 - x3, 2) + math.pow(y2 - y3, 2))
    ratio = 0
    if len1 != 0:
        ratio = round(len2/len1, 2)
    print(ratio)
    return ratio


def get_angle(x1, y1, x2, y2, x3, y3):
    angle = 0
    m1 = 0
    m2 = 0
    if x1 - x2 != 0:
        m1 = ((y1 - y2) / (x1 - x2))
    if x1 - x3 != 0:
        m2 = ((y1 - y3) / (x1 - x3))
    if 1 + (m2 * m1) != 0:
        angle = math.atan((m1 - m2) / (1 + (m1 * m2)))
        angle = round(math.degrees(angle))
    return angle


def volume_control(img, volume, incr):
    max_vol = 100
    min_vol = 0

    # bounds volume
    if volume > max_vol:
        volume = 100
    if volume < min_vol:
        volume = 0

    # increments volume
    if incr <= -2 or incr >= 2:
        volume = round(volume + incr/4)

    # draws visual
    cv2.rectangle(img, (20, 20), (40, 120), (255, 127, 0), 2)
    cv2.rectangle(img, (20, 120-volume), (40, 120), (255, 127, 0), -1)

    return volume


def main():
    ht = HandRecognition()
    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        img = ht.track_hand(img)
        lmList = ht.get_landmarks_positions(img)
        cv2.imshow("Camera", img)
        cv2.waitKey(1)

        ratio = test_ratio(img, lmList)
<<<<<<< HEAD
        lower_bound = 0.3
=======
        lower_bound = 0.30
>>>>>>> 46381dd8ce5fae6a8f8906a93b215edd7c836d9d
        upper_bound = 0.75

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[12][1], lmList[12][2]
        volume = 50

        # detect gesture
        while lower_bound <= ratio <= upper_bound:
            success, img = cap.read()
            img = ht.track_hand(img)
            lmList = ht.get_landmarks_positions(img)

            x3, y3 = lmList[12][1], lmList[12][2]
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.line(img, (x1, y1), (x3, y3), (255, 127, 0), 3)

            angle = get_angle(x1, y1, x2, y2, x3, y3)
            increment = round(angle/5)
            volume = volume_control(img, volume, increment)

            print(ratio, ", ", angle)
            ratio = test_ratio(img, lmList)

            cv2.imshow("Camera", img)
            cv2.waitKey(1)

        print("no gesture recognized")


if __name__ == "__main__":
    main()
