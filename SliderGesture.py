import cv2
import math
import HandTracker


class SliderGesture():
    def __init__(self, default_value=50, flip_direction=False):
        self.ht = HandTracker.HandRecognition()
        self.slider_position = default_value
        self.flip_direction = flip_direction

    def draw_gesture(self, img, x1, y1, x2, y2):
        cv2.line(img, (x1, y1), (x2, y2), (255, 127, 0), 3)

    def detect(self, lm_list, lower_bound=1, upper_bound=40):
        if not lm_list:
            return False
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]
        distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        if distance != 0:
            return lower_bound <= distance <= upper_bound
        return False

    def get_horizontal_distance(self, x1, y1, x2, y2):
        distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        if not self.flip_direction:
            if x1 > x2:
                distance = -distance
        else:
            if x1 < x2:
                distance = -distance
        return distance

    def execute(self, capture, lm_list, hand_num, threshold=True):
        x1, y1 = lm_list[4][1], lm_list[4][2]
        while threshold:
            success, img = capture.read()
            img = cv2.flip(img, 1)
            img = self.ht.track_hand(img)
            if self.ht.count_hands() != hand_num + 1:
                break
            lm_list = self.ht.get_landmarks_positions()[hand_num]

            # processes and executes instruction
            x2, y2 = lm_list[4][1], lm_list[4][2]
            self.draw_gesture(img, x1, y1, x2, y2)
            dist = self.get_horizontal_distance(x1, y1, x2, y2)
            new_slider_position = self.slider_control(img, self.slider_position, dist)
            if self.slider_position != new_slider_position:
                self.slider_position = new_slider_position
                x1, y1 = lm_list[4][1], lm_list[4][2]

            threshold = self.detect(lm_list)
            cv2.imshow("Camera", img)
            cv2.waitKey(1)

    def slider_control(self, img, slider_position, dist, max_dist=100, min_dist=0, scale=0.2, slider_incr=2):
        # increments volume
        incr = round(dist * scale)
        if incr <= -slider_incr or incr >= slider_incr:
            slider_position = slider_position + incr

        # bounds volume
        if slider_position > max_dist:
            slider_position = max_dist
        if slider_position < min_dist:
            slider_position = min_dist

        # draws visual
        cv2.line(img, (20, 20), (220, 20), (255, 127, 0), 2)
        cv2.line(img, (20, 15), (20, 25), (255, 127, 0), 2)
        cv2.line(img, (220, 15), (220, 25), (255, 127, 0), 2)
        cv2.circle(img, (20 + 2*slider_position, 20), 5, (255, 127, 0), cv2.FILLED)
        return slider_position
