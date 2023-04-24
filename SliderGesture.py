import cv2
import math
import HandTracker
import time


class SliderGesture:
    def __init__(self, default_value=50, invert_controls=False):
        self.ht = HandTracker.HandRecognition()
        self.slider_position = default_value
        self.invert_controls = invert_controls

    def detect(self, lm_list, lower_bound=1, upper_bound=20):
        # threshold is the distance between the thumb and index fingers
        if not lm_list:
            return False
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]
        distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        return lower_bound <= distance <= upper_bound

    def execute(self, capture, lm_list, hand_num, hand_count, scale=0.4, min_incr=1, threshold=True):
        incr = 0
        x1, y1 = lm_list[4][1], lm_list[4][2]
        # provide a 0.1-second buffer when the threshold fails
        start_time = time.time()
        while (threshold and -min_incr < incr < min_incr) or (time.time() - start_time < 0.1):
            success, img = capture.read()
            img = cv2.flip(img, 1)
            img = self.ht.track_hand(img)
            if self.ht.count_hands() != hand_count:
                break

            # processes and executes instruction
            lm_list = self.ht.get_landmarks_positions()[hand_num]
            x2, y2 = lm_list[4][1], lm_list[4][2]
            dist = self.get_horizontal_distance(x1, x2)
            incr = scale * dist
            if incr <= -min_incr or incr >= min_incr:
                self.slider_control(img, incr)
                x1, y1 = x2, y2

            self.draw_gesture(img, x1, y1, x2, y2)
            threshold = self.detect(lm_list)
            cv2.imshow("Camera", img)
            cv2.waitKey(1)
            if threshold:
                start_time = time.time()
        return

    def slider_control(self, img, dist, max_dist=100, min_dist=0, slider_incr=1):
        # slides slider
        incr = round(dist * slider_incr)
        self.slider_position = self.slider_position + incr

        # bounds slider
        if self.slider_position > max_dist:
            self.slider_position = max_dist
        if self.slider_position < min_dist:
            self.slider_position = min_dist

        # draws visual
        cv2.line(img, (20, 20), (220, 20), (255, 127, 0), 2)
        cv2.line(img, (20, 15), (20, 25), (255, 127, 0), 2)
        cv2.line(img, (220, 15), (220, 25), (255, 127, 0), 2)
        cv2.circle(img, (20 + (2 * self.slider_position), 20), 5, (255, 127, 0), cv2.FILLED)

    def get_horizontal_distance(self, x1, x2):
        if not self.invert_controls:
            distance = x2 - x1
        else:
            distance = x1 - x2
        return distance

    def draw_gesture(self, img, x1, y1, x2, y2):
        cv2.line(img, (x1, y1), (x2, y2), (255, 127, 0), 3)
