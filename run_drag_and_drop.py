import cv2
import math
import HandTracker
import DesktopControl


# --------------------------------
hand_num = 0
# --------------------------------


def move_mouse(img, x_incr, y_incr):
    x_incr = round(x_incr)
    y_incr = round(y_incr)
    desktop.move_mouse_rel(x_incr, y_incr)

    # draws visual
    draw_tracking(img)


def pinch(img, action):
    if action == "click" or action == "Click":
        desktop.left_click()
        draw_pinch(img)
    elif action == "hold" or action == "Hold":
        desktop.hold_left_click()


def get_distance(x1, y1, x2, y2):
    distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
    return distance


def get_midpoint(x1, y1, x2, y2):
    x = round((x1 + x2) / 2)
    y = round((y1 + y2) / 2)
    return x, y


def draw_tracking(img):
    x, y = desktop.get_mouse_position()
    cv2.circle(img, (x, y), 5, (255, 127, 0), cv2.FILLED)


def draw_pinch(img):
    x, y = desktop.get_mouse_position()
    cv2.circle(img, (x, y), 20, (0, 255, 0), 2)


def draw_hold(img):
    x, y = desktop.get_mouse_position()
    cv2.circle(img, (x, y), 20, (0, 255, 255), 2)


cam_width, cam_height = 640, 360
capture = cv2.VideoCapture(0)
capture.set(3, cam_width)
capture.set(4, cam_height)
ht = HandTracker.HandRecognition()
desktop = DesktopControl.DesktopControl()

action = "click"
dictionary = {
    1: 8,
    2: 12,
    3: 16,
}
pinch_fingers = [1, 2]
pinch_bound = 20
scale = 2
min_incr = 1

while True:
    success, img = capture.read()
    img = cv2.flip(img, 1)
    ht.track_hand(img)
    cv2.imshow("Camera", img)
    cv2.waitKey(1)
    hand_count = ht.count_hands()

    if ht.count_hands() != 0:
        lm_list = ht.get_landmarks_positions()[hand_num]
        x0, y0 = lm_list[4][1], lm_list[4][2]
        mdpt_orig = get_midpoint(x0, y0, lm_list[12][1], lm_list[12][2])

    while ht.count_hands() != 0:
        success, img = capture.read()
        img = cv2.flip(img, 1)
        img = ht.track_hand(img)
        if ht.count_hands() == 0:
            break
        if ht.count_hands() != hand_count:
            hand_num = hand_num + (ht.count_hands() - hand_count)

        hand_count = ht.count_hands()
        lm_list = ht.get_landmarks_positions()[hand_num]
        x0, y0 = lm_list[4][1], lm_list[4][2]
        mdpt_new = get_midpoint(x0, y0, lm_list[12][1], lm_list[12][2])
        x_diff = (mdpt_new[0] - mdpt_orig[0]) / scale
        y_diff = (mdpt_new[1] - mdpt_orig[1]) / scale
        if x_diff <= -min_incr or x_diff >= min_incr:
            move_mouse(img, x_diff, y_diff)
            mdpt_orig = mdpt_new
        elif y_diff <= -min_incr or y_diff >= min_incr:
            move_mouse(img, x_diff, y_diff)
            mdpt_orig = mdpt_new

        # detects for pinch gesture
        dist_list = []
        for i in pinch_fingers:
            lm = dictionary[i]
            x1, y1 = lm_list[lm][1], lm_list[lm][2]
            dist = get_distance(x0, y0, x1, y1)
            dist_list.append(dist)
        for dist in dist_list:
            if dist < pinch_bound:
                # executes pinch gesture
                pinch(img, action)
                break

        cv2.imshow("Camera", img)
        cv2.waitKey(1)
