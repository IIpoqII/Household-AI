import cv2
import math
import HandTracker
import time


class RotateHandGesture:
    def __init__(self, volume=50, invert_controls=False):
        self.ht = HandTracker.HandRecognition()
        self.volume = volume
        self.invert_controls = invert_controls

    def detect(self, lm_list, lower_bound=0.45, upper_bound=0.75):
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

    def execute(self, capture, lm_list, hand_num, hand_count, scale=2, min_incr=1, threshold=True):
        # scale affects the physical_movement:rotation ratio
        # higher means rotating the "knob" requires more physical movement
        incr = 0
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[12][1], lm_list[12][2]
        start_time = time.time()
        while (threshold and -min_incr < incr < min_incr) or (time.time() - start_time < 1):
            if threshold:
                start_time = time.time()
            success, img = capture.read()
            img = cv2.flip(img, 1)
            img = self.ht.track_hand(img)
            if self.ht.count_hands() != hand_count:
                break

            # processes and executes instruction
            lm_list = self.ht.get_landmarks_positions()[hand_num]
            x3, y3 = lm_list[12][1], lm_list[12][2]
            angle = self.get_angle(x1, y1, x2, y2, x3, y3)
            incr = angle / scale
            if incr <= -min_incr or incr >= min_incr:
                self.volume_control(img, incr)
                x1, y1 = lm_list[4][1], lm_list[4][2]
                x2, y2 = x3, y3

            self.draw_gesture(img, x1, y1, x2, y2, x3, y3)
            threshold = self.detect(lm_list)
            cv2.imshow("Camera", img)
            cv2.waitKey(1)
        return

    def volume_control(self, img, incr, max_vol=100, min_vol=0, knob_incr=1):
        # increments volume
        incr = round(incr * knob_incr)
        self.volume = self.volume + incr

        # bounds volume
        if self.volume > max_vol:
            self.volume = max_vol
        if self.volume < min_vol:
            self.volume = min_vol

        # draws visual
        cv2.rectangle(img, (20, 20), (40, 120), (255, 127, 0), 2)
        cv2.rectangle(img, (20, 120 - self.volume), (40, 120), (255, 127, 0), -1)

    def get_angle(self, x1, y1, x2, y2, x3, y3):
        angle = 0
        m1 = 0
        m2 = 0
        if x1 - x2 != 0:
            m1 = ((y1 - y2) / (x1 - x2))
        if x1 - x3 != 0:
            m2 = ((y1 - y3) / (x1 - x3))
        if 1 + (m2 * m1) != 0:
            if not self.invert_controls:
                angle = math.atan((m2 - m1) / (1 + (m2 * m1)))
            else:
                angle = math.atan((m1 - m2) / (1 + (m1 * m2)))
            angle = math.degrees(angle)
        return angle

    def draw_trigger(self, img, x1, y1, x2, y2, x3, y3):
        cv2.line(img, (x1, y1), (x2, y2), (255, 127, 0), 3)
        cv2.line(img, (x2, y2), (x3, y3), (255, 127, 0), 3)

    def draw_gesture(self, img, x1, y1, x2, y2, x3, y3):
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.line(img, (x1, y1), (x3, y3), (255, 127, 0), 3)
