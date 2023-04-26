import cv2
import math
import HandTracker
import DesktopControl


# --------------------------------
UI_scale = 0.95
maintain_tracking = True
hand_num = 0
# --------------------------------


def detect(hand, upper_bound=120):
    lm_list = hand.lm_list
    x0, y0 = lm_list[4][1], lm_list[4][2]
    x1, y1 = lm_list[8][1], lm_list[8][2]
    x2, y2 = lm_list[12][1], lm_list[12][2]
    dist1 = get_distance(x0, y0, x1, y1)
    dist2 = get_distance(x0, y0, x2, y2)
    return dist1 < upper_bound and dist2 < upper_bound


def move_mouse(x, y):
    x = round(x)
    y = round(y)
    pos = (x, y)
    pos = list(pos)
    pos = bound_to_screen(pos)
    pos = adjust_for_corner_failsafe(pos)
    desktop.move_mouse(pos[0], pos[1])


def move_mouse_rel(x_incr, y_incr):
    x_incr = round(x_incr)
    y_incr = round(y_incr)
    pos = list(desktop.get_mouse_position())
    pos[0] = pos[0] + x_incr
    pos[1] = pos[1] + y_incr
    pos = bound_to_screen(pos)
    adjust_for_corner_failsafe(pos)
    print(pos)
    desktop.move_mouse_rel(x_incr, y_incr)


def bound_to_screen(pos):
    pos[0] = max(0, min(screen_w, pos[0]))
    pos[1] = max(0, min(screen_h, pos[1]))
    return pos


def adjust_for_corner_failsafe(pos):
    if pos[0] <= 0:
        pos[1] = 1
    if pos[1] <= 0:
        pos[0] = 1
    if pos[0] >= screen_w:
        pos[1] = screen_w - 20
    if pos[1] >= screen_h:
        pos[0] = screen_h - 20
    return pos


def pinch(action):
    if action == "click" or action == "Click":
        desktop.left_click()
    elif action == "hold" or action == "Hold":
        desktop.hold_left_click()


def get_distance(x1, y1, x2, y2):
    distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
    return distance


def get_midpoint(x1, y1, x2, y2):
    x = round((x1 + x2) / 2)
    y = round((y1 + y2) / 2)
    return x, y


def draw_gesture(img, x, y):
    cv2.circle(img, (x, y), 5, (255, 127, 0), cv2.FILLED)


def draw_pinch(img, x, y):
    cv2.circle(img, (x, y), 20, (0, 255, 0), 2)


def draw_hold(img):
    x, y = desktop.get_mouse_position()
    cv2.circle(img, (x, y), 20, (0, 255, 255), 2)


def test_UI_bounded(x1, y1):
    return UI_box[0][0] < x1 < UI_box[1][0] and UI_box[0][1] < y1 < UI_box[1][1]


def draw_bounded_area(img):
    cv2.rectangle(img, (UI_box[0][0], UI_box[0][1]), (UI_box[1][0], UI_box[1][1]), (0, 255, 0), 2)


cam_width, cam_height = 1280, 720
capture = cv2.VideoCapture(0)
capture.set(3, cam_width)
capture.set(4, cam_height)
ht = HandTracker.HandRecognition()
desktop = DesktopControl.DesktopControl()
screen_w, screen_h = desktop.get_screen_size()

action = "click"
dictionary = {
    1: 8,
    2: 12,
    3: 16,
}
pinch_fingers = [1, 2]
pinch_bound = 40
sens = 4
min_incr = 2

# bounding box for the UI area
x_ratio = screen_w / cam_width
y_ratio = screen_h / cam_height
if x_ratio > y_ratio:
    ratio = x_ratio
else:
    ratio = y_ratio

x_screen_diff = round((1 - UI_scale) * (screen_w / ratio))
y_screen_diff = round((1 - UI_scale) * (screen_h / ratio))
UI_box = (x_screen_diff - 1, y_screen_diff - 1), ((cam_width - x_screen_diff - 1), (cam_height - y_screen_diff - 1))

while True:
    success, img = capture.read()
    img = cv2.flip(img, 1)
    ht.track_hand(img, draw=False, identify_hand_num=True)
    cv2.imshow("Camera", img)
    cv2.waitKey(1)

    hands_list = ht.get_hands()
    hand_count = ht.count_hands()

    if len(hands_list) > 0:
        for hand in hands_list:
            threshold = detect(hand)
            if threshold:
                hand_num = hands_list.index(hand)
                lm_list = ht.get_landmarks_positions()[hand_num]
                x0, y0 = lm_list[4][1], lm_list[4][2]
                mdpt_orig = get_midpoint(x0, y0, lm_list[12][1], lm_list[12][2])
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
                while threshold:
                    success, img = capture.read()
                    img = cv2.flip(img, 1)
                    img = ht.track_hand(img, draw=False, identify_hand_num=True)
                    hand_count_new = ht.count_hands()
                    if hand_count_new == 0:
                        break
                    if hand_count_new != hand_count:
                        if maintain_tracking:
                            hand_num = hand_num + (hand_count_new - hand_count)
                            hand_count = hand_count_new
                        else:
                            break
                    draw_bounded_area(img)

                    # track position
                    hand = ht.get_hands()[hand_num]
                    lm_list = hand.lm_list
                    x0, y0 = lm_list[4][1], lm_list[4][2]
                    mdpt_new = get_midpoint(x0, y0, lm_list[12][1], lm_list[12][2])
                    x_diff = ratio * (mdpt_new[0] - mdpt_orig[0])
                    y_diff = ratio * (mdpt_new[1] - mdpt_orig[1])
                    if x_diff <= -min_incr or x_diff >= min_incr or y_diff <= -min_incr or y_diff >= min_incr:
                        UI_mdpt = mdpt_new[0] - x_screen_diff, mdpt_new[1] - y_screen_diff
                        move_mouse(UI_mdpt[0] * ratio / (UI_scale - (1-UI_scale)), UI_mdpt[1] * ratio / (UI_scale - (1-UI_scale)))
                        mdpt_orig = mdpt_new

                    # detect for pinch gesture
                    dist_list = []
                    for i in pinch_fingers:
                        lm = dictionary[i]
                        x1, y1 = lm_list[lm][1], lm_list[lm][2]
                        dist = get_distance(x0, y0, x1, y1)
                        dist_list.append(dist)
                    for dist in dist_list:
                        if dist < pinch_bound:
                            # executes pinch gesture
                            pinch(action)
                            if action == "click" or action == "Click":
                                draw_pinch(img, mdpt_new[0], mdpt_new[1])
                            elif action == "hold" or action == "Hold":
                                draw_hold(img, mdpt_new[0], mdpt_new[1])
                            break

                    draw_gesture(img, mdpt_new[0], mdpt_new[1])
                    threshold = detect(hand)
                    cv2.imshow("Camera", img)
                    cv2.waitKey(1)
                break
