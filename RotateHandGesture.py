import cv2
import math
import HandTracker


class RotateHandGesture():
    def __init__(self, volume=50, flip_direction=False):
        self.ht = HandTracker.HandRecognition()
        self.volume = volume
        self.flip_direction = flip_direction

    def draw_gesture(self, img, x1, y1, x2, y2, x3, y3):
        cv2.line(img, (x1, y1), (x2, y2), (255, 127, 0), 3)
        cv2.line(img, (x2, y2), (x3, y3), (255, 127, 0), 3)

    def detect(self, lm_list, lower_bound=0.30, upper_bound=0.75):
        if not lm_list:
            return False
        ratio = 0
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]
        x3, y3 = lm_list[12][1], lm_list[12][2]
        len1 = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        len2 = math.sqrt(math.pow(x2 - x3, 2) + math.pow(y2 - y3, 2))
        if len1 != 0:
            ratio = round(len2 / len1, 2)
        return lower_bound <= ratio <= upper_bound

    def get_angle(self, x1, y1, x2, y2, x3, y3):
        angle = 0
        m1 = 0
        m2 = 0
        if x1 - x2 != 0:
            m1 = ((y1 - y2) / (x1 - x2))
        if x1 - x3 != 0:
            m2 = ((y1 - y3) / (x1 - x3))
        if 1 + (m2 * m1) != 0:
            if not self.flip_direction:
                angle = math.atan((m2 - m1) / (1 + (m2 * m1)))
            else:
                angle = math.atan((m1 - m2) / (1 + (m1 * m2)))
            angle = round(math.degrees(angle))
        return angle

    def draw_angle(self, img, x1, y1, x2, y2, x3, y3):
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.line(img, (x1, y1), (x3, y3), (255, 127, 0), 3)

    def execute(self, capture, lm_list, hand_num, threshold=True):
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[12][1], lm_list[12][2]
        while threshold:
            success, img = capture.read()
            img = cv2.flip(img, 1)
            img = self.ht.track_hand(img)
            if self.ht.count_hands() != hand_num + 1:
                break
            lm_list = self.ht.get_landmarks_positions()[hand_num]

            # processes and executes instruction
            x3, y3 = lm_list[12][1], lm_list[12][2]
            # cv2.line(img, (x1, y1), (x2, y2), (255, 127, 0), 3)
            # cv2.line(img, (x2, y2), (x3, y3), (255, 127, 0), 3)
            angle = self.get_angle(x1, y1, x2, y2, x3, y3)
            new_volume = self.volume_control(img, self.volume, angle)
            if self.volume != new_volume:
                self.volume = new_volume
                x1, y1 = lm_list[4][1], lm_list[4][2]
                x2, y2 = lm_list[12][1], lm_list[12][2]

            threshold = self.detect(lm_list)
            self.draw_angle(img, x1, y1, x2, y2, x3, y3)
            cv2.imshow("Camera", img)
            cv2.waitKey(1)

    def volume_control(self, img, volume, angle, max_vol=100, min_vol=0, scale=1, knob_incr=4):
        # increments volume
        incr = round(angle * scale)
        if incr <= -knob_incr or incr >= knob_incr:
            volume = volume + incr

        # bounds volume
        if volume > max_vol:
            volume = max_vol
        if volume < min_vol:
            volume = min_vol

        # draws visual
        cv2.rectangle(img, (20, 20), (40, 120), (255, 127, 0), 2)
        cv2.rectangle(img, (20, 120 - volume), (40, 120), (255, 127, 0), -1)
        return volume
