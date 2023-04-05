import cv2
import mediapipe as mp
import numpy as np


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

    def get_hand_orientation(self, img):
        lmList = self.get_landmarks_positions(img)

        pts = np.asarray([lmList[0], lmList[5], lmList[17]])
        normal_vector = (np.cross(pts[2]-pts[0], pts[1]-pts[2])).astype('float64')
        normal_vector /= np.linalg.norm(normal_vector)

        return normal_vector

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


def main():
    camera = HandRecognition()
    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        img = camera.track_hand(img)
        lmList = camera.get_landmarks_positions(img)
        print(camera.get_hand_orientation(img))

        cv2.imshow("Camera", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
