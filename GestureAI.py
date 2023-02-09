import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)

# mediapipe module for
mpHands = mp.solutions.hands
hands = mpHands.Hands(False, 2, 0.5, 0.5)
mpDraw = mp.solutions.drawing_utils

while True:
    img = cap.read()

    # convert camera feed to RGB
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(imgRGB)

    # visualize multiple hand
    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:

            # identifies landmarks on each hand
            for id, lm in enumerate(hand.landmark):
                h,w,c = img.shape
                cx, cy = int(lm.x*w), int (lm.y*h)

                # highlight root of palm
                if id == 0:
                    cv2.circle(img, (cx,cy), 10, (255,0,255), cv2.FILLED)

                # highlight tip of thumb
                if id == 4:
                    cv2.circle(img, (cx,cy), 10, (255,0,255), cv2.FILLED)

            mpDraw.draw_landmarks(img, hand, mpHands.HAND_CONNECTIONS)

    cv2.imshow("Camera", img)
    cv2.waitKey(1)
