import cv2
import mediapipe as mp
import numpy as np
import types
from google.protobuf.json_format import MessageToDict


class HandRecognition:
    def __init__(self, mode=False, max_hands=4, complexity=1, detection_confidence=0.6, tracking_confidence=0.6):
        self.results = None

        self.mode = mode
        self.maxHands = max_hands
        self.complexity = complexity
        self.detectionConf = detection_confidence
        self.trackingConf = tracking_confidence

        self.mpHands = mp.solutions.hands
        self.recognized_hands = self.mpHands.Hands(self.mode, self.maxHands, self.complexity, self.detectionConf, self.trackingConf)
        self.mpDraw = mp.solutions.drawing_utils

        # hands_list stores hand objects with attributes lm_list, orientation, handedness
        self.hands_list = []

    def track_hand(self, img, draw=True, identify_hand_num=False, cirRad=5, cirBGR=(255, 127, 0)):
        # convert camera feed to RGB and identify hand
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.recognized_hands.process(imgRGB)
        self.hands_list = []

        # visualize multiple hand
        if self.results.multi_hand_landmarks:
            # get data on each hand
            multi_hand_landmarks = self.results.multi_hand_landmarks
            multi_handedness_list = self.results.multi_handedness
            n = len(multi_hand_landmarks) - 1
            for i in range(n, -1, -1):
                hand_num = multi_hand_landmarks[i]
                if draw:
                    self.mpDraw.draw_landmarks(img, hand_num, self.mpHands.HAND_CONNECTIONS)
                hand = types.SimpleNamespace()

                # get hand landmarks
                lm_list = []
                for lmID, lm in enumerate(hand_num.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([lmID, cx, cy])
                    if draw:
                        # highlight root of palm, tip of thumb, tip of index, tip of middle, tip of ring, tip of pinky
                        if (lmID == 0) or (lmID == 4) or (lmID == 8) or (lmID == 12) or (lmID == 16) or (lmID == 20):
                            cv2.circle(img, (cx, cy), cirRad, cirBGR, cv2.FILLED)
                hand.lm_list = lm_list

                # get hand orientation
                pts = np.asarray([lm_list[0], lm_list[5], lm_list[17]])
                normal_vector = (np.cross(pts[2] - pts[0], pts[1] - pts[2])).astype('float64')
                normal_vector /= np.linalg.norm(normal_vector)
                hand.orientation = normal_vector

                # get handedness
                label = MessageToDict(multi_handedness_list[i])['classification'][0]['label']
                if label == "Left":
                    hand.handedness = "Left"
                elif label == "Right":
                    hand.handedness = "Right"
                else:
                    hand.handedness = "Error"
                self.hands_list.append(hand)
            if identify_hand_num:
                self.identify_hand_num(img)
        return img

    def count_hands(self):
        return len(self.hands_list)

    def get_hands(self):
        return self.hands_list

    def get_landmarks_positions(self):
        # hands_list[] is a list of landmarks, which is a list of the landmark ID and position
        # hands_list[] is a list[list[]]
        hands_list = []
        for hand in self.hands_list:
            hands_list.append(hand.lm_list)
        return hands_list

    def get_hand_orientation(self):
        # hands_list[] is a list of orientations for each hand
        hands_list = []
        for hand in self.hands_list:
            hands_list.append(hand.orientation)
        return hands_list

    def get_handedness(self):
        # hands_list[] is a list of handedness for each hand
        hands_list = []
        for hand in self.hands_list:
            hands_list.append(hand.handedness)
        return hands_list

    def print_hand(self, print_lm_list=False, print_orientation=False, print_handedness=False):
        hands_list = self.get_hands()
        for hand in hands_list:
            print("Hand", hands_list.index(hand))
            if print_lm_list:
                print("      ", hand.lm_list)
            if print_orientation:
                print("      ", hand.orientation)
            if print_handedness:
                print("      ", hand.handedness)
        if hands_list:
            print()
        return

    def identify_hand_num(self, img):
        hands_list = self.get_hands()
        for hand in hands_list:
            x, y = hand.lm_list[8][1], hand.lm_list[8][2]
            text = "Hand " + str(hands_list.index(hand))
            img = cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        return img


def test():
    cam_width, cam_height = 1280, 720
    capture = cv2.VideoCapture(0)
    capture.set(3, cam_width)
    capture.set(4, cam_height)
    ht = HandRecognition()

    while True:
        success, img = capture.read()
        img = cv2.flip(img, 1)
        img = ht.track_hand(img, identify_hand_num=True)

        cv2.imshow("Camera", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    test()
