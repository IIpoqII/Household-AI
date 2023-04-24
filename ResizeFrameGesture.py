import cv2
import math
import HandTracker
import time


class ResizeFrameGesture:
    def __init__(self, default_value=((300, 100), (500, 400)), invert_controls=False):
        self.ht = HandTracker.HandRecognition()
        self.frame_position = default_value
        self.invert_controls = invert_controls

    def detect(self, hand_left, hand_right, lower_bound=30):
        # threshold is the angle between the thumb and index fingers of both hands
        if not hand_left.lm_list or not hand_right.lm_list:
            return False
        if hand_left.handedness == "Left" and hand_right.handedness == "Right":
            lm_list_left = hand_left.lm_list
            lm_list_right = hand_right.lm_list
            x1_l, y1_l = lm_list_left[0][1], lm_list_left[0][2]
            x2_l, y2_l = lm_list_left[4][1], lm_list_left[4][2]
            x3_l, y3_l = lm_list_left[8][1], lm_list_left[8][2]
            x1_r, y1_r = lm_list_right[0][1], lm_list_right[0][2]
            x2_r, y2_r = lm_list_right[4][1], lm_list_right[4][2]
            x3_r, y3_r = lm_list_right[8][1], lm_list_right[8][2]
            angle_left = abs(self.get_angle(x1_l, y1_l, x2_l, y2_l, x3_l, y3_l))
            angle_right = abs(self.get_angle(x1_r, y1_r, x2_r, y2_r, x3_r, y3_r))
            if angle_left != 0 and angle_right != 0:
                if angle_left > lower_bound and angle_right > lower_bound:
                    return True
        return False

    def detect_move_gesture(self, lm_list_left, lm_list_right, upper_bound=30):
        # threshold is a closed fist for both hands
        x1_l, y1_l = lm_list_left[3][1], lm_list_left[3][2]
        x2_l, y2_l = lm_list_left[7][1], lm_list_left[7][2]
        x1_r, y1_r = lm_list_right[3][1], lm_list_right[3][2]
        x2_r, y2_r = lm_list_right[7][1], lm_list_right[7][2]
        dist_l = self.get_distance(x1_l, y1_l, x2_l, y2_l)
        dist_r = self.get_distance(x1_r, y1_r, x2_r, y2_r)
        return dist_l < upper_bound and dist_r < upper_bound

    def execute(self, capture, hand_left, hand_right, hand_left_num, hand_right_num, hand_count, scale=2, min_size_incr=1, min_move_incr=2, threshold=True):
        dist_diff = 0
        lm_list_left = hand_left.lm_list
        lm_list_right = hand_right.lm_list
        x1, y1 = lm_list_left[0][1], lm_list_left[0][2]
        x2, y2 = lm_list_right[0][1], lm_list_right[0][2]
        dist_orig = self.get_distance(x1, y1, x2, y2)
        mdpt_orig = self.get_midpoint(x1, y1, x2, y2)
        # provide a 2-second buffer when the threshold fails
        start_time = time.time()
        while (threshold and -min_size_incr < dist_diff < min_size_incr) or (time.time() - start_time < 2):
            success, img = capture.read()
            img = cv2.flip(img, 1)
            img = self.ht.track_hand(img)
            if self.ht.count_hands() != hand_count:
                break

            # processes and executes instruction for the resize frame gesture
            left_hand = self.ht.get_hands()[hand_left_num]
            right_hand = self.ht.get_hands()[hand_right_num]
            lm_list_left = self.ht.get_landmarks_positions()[hand_left_num]
            lm_list_right = self.ht.get_landmarks_positions()[hand_right_num]
            x1, y1 = lm_list_left[0][1], lm_list_left[0][2]
            x2, y2 = lm_list_right[0][1], lm_list_right[0][2]
            dist_new = self.get_distance(x1, y1, x2, y2)
            dist_diff = scale * (dist_new - dist_orig)
            mdpt_new = self.get_midpoint(x1, y1, x2, y2)
            if dist_diff <= -min_size_incr or dist_diff >= min_size_incr:
                self.resize_frame_control(img, dist_diff)
                dist_orig = dist_new

            # processes and executes instruction for the move frame gesture
            mdpt_orig = self.get_midpoint(x1, y1, x2, y2)
            lm_list_left = self.ht.get_landmarks_positions()[hand_left_num]
            lm_list_right = self.ht.get_landmarks_positions()[hand_right_num]
            while self.detect_move_gesture(lm_list_left, lm_list_right):
                success, img = capture.read()
                img = cv2.flip(img, 1)
                img = self.ht.track_hand(img)
                if self.ht.count_hands() != hand_count:
                    break

                lm_list_left = self.ht.get_landmarks_positions()[hand_left_num]
                lm_list_right = self.ht.get_landmarks_positions()[hand_right_num]
                x1, y1 = lm_list_left[0][1], lm_list_left[0][2]
                x2, y2 = lm_list_right[0][1], lm_list_right[0][2]
                mdpt_new = self.get_midpoint(x1, y1, x2, y2)
                x_diff = (mdpt_new[0] - mdpt_orig[0]) / scale
                y_diff = (mdpt_new[1] - mdpt_orig[1]) / scale
                if x_diff <= -min_move_incr or x_diff >= min_move_incr:
                    self.move_frame_control(img, x_diff, y_diff)
                    mdpt_orig = mdpt_new
                elif y_diff <= -min_move_incr or y_diff >= min_move_incr:
                    self.move_frame_control(img, x_diff, y_diff)
                    mdpt_orig = mdpt_new
                self.draw_gesture(img, x1, y1, x2, y2, mdpt_new)
                start_time = time.time()
                cv2.imshow("Camera", img)
                cv2.waitKey(1)

            # self.draw_trigger(img, left_hand, right_hand)
            self.draw_gesture(img, x1, y1, x2, y2, mdpt_new)
            threshold = self.detect(hand_left, hand_right)
            cv2.imshow("Camera", img)
            cv2.waitKey(1)
            if threshold:
                start_time = time.time()
        return

    def resize_frame_control(self, img, incr, max_size=100, min_size=20, frame_incr=1):
        # controls frame size
        incr = round(incr * frame_incr)
        x1, y1 = self.frame_position[0][0], self.frame_position[0][1]
        x2, y2 = self.frame_position[1][0], self.frame_position[1][1]
        x1 = x1 - incr
        y1 = y1 - incr
        x2 = x2 + incr
        y2 = y2 + incr
        self.frame_position = ((x1, y1), (x2, y2))

        # draws visual
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 127, 0), 2)

    def move_frame_control(self, img, x_incr, y_incr, pos_incr=1):
        # controls frame position
        x_incr = round(x_incr * pos_incr)
        y_incr = round(y_incr * pos_incr)
        x1, y1 = self.frame_position[0][0], self.frame_position[0][1]
        x2, y2 = self.frame_position[1][0], self.frame_position[1][1]
        x1 = x1 + x_incr
        y1 = y1 + y_incr
        x2 = x2 + x_incr
        y2 = y2 + y_incr
        self.frame_position = ((x1, y1), (x2, y2))

        # draws visual
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 127, 0), 2)

    def get_angle(self, x1, y1, x2, y2, x3, y3):
        # uses (x1, y1) as the vertex
        angle = 0
        m1 = 0
        m2 = 0
        if x1 - x2 != 0:
            m1 = ((y1 - y2) / (x1 - x2))
        if x1 - x3 != 0:
            m2 = ((y1 - y3) / (x1 - x3))
        if 1 + (m2 * m1) != 0:
            angle = math.atan((m2 - m1) / (1 + (m2 * m1)))
            angle = round(math.degrees(angle))
        return angle

    def get_distance(self, x1, y1, x2, y2):
        distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        return distance

    def get_midpoint(self, x1, y1, x2, y2):
        x = round((x1 + x2) / 2)
        y = round((y1 + y2) / 2)
        return x, y

    def draw_trigger(self, img, hand_left, hand_right):
        lm_list_left = hand_left.lm_list
        lm_list_right = hand_right.lm_list
        x1_l, y1_l = lm_list_left[0][1], lm_list_left[0][2]
        x2_l, y2_l = lm_list_left[4][1], lm_list_left[4][2]
        x3_l, y3_l = lm_list_left[8][1], lm_list_left[8][2]
        x1_r, y1_r = lm_list_right[0][1], lm_list_right[0][2]
        x2_r, y2_r = lm_list_right[4][1], lm_list_right[4][2]
        x3_r, y3_r = lm_list_right[8][1], lm_list_right[8][2]
        cv2.line(img, (x1_l, y1_l), (x2_l, y2_l), (255, 127, 0), 3)
        cv2.line(img, (x1_l, y1_l), (x3_l, y3_l), (255, 127, 0), 3)
        cv2.line(img, (x1_r, y1_r), (x2_r, y2_r), (255, 127, 0), 3)
        cv2.line(img, (x1_r, y1_r), (x3_r, y3_r), (255, 127, 0), 3)

    def draw_gesture(self, img, x1, y1, x2, y2, mdpt):
        cv2.line(img, (x1, y1), (x2, y2), (255, 127, 0), 3)
        cv2.circle(img, (mdpt[0], mdpt[1]), 5, (255, 127, 0), cv2.FILLED)
