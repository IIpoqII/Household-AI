import cv2
import mediapipe as mp

class HandRecognition():
    def __int__(self, mode=False, maxHands=2, detectionConf=0.5, trackingConf=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionConf = detectionConf
        self.trackingConf = trackingConf

        # mediapipe module for
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.detectionConf, self.trackingConf)
        self.mpDraw = mp.solutions.drawing_utils

    def handPosition(self, img, draw = True):
        # convert camera feed to RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = self.hands.process(imgRGB)

        # visualize multiple hand
        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                     
                # identifies landmarks on each hand
                for id, lm in enumerate(hand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)

                    # highlight root of palm
                    if id == 0:
                        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
                    # highlight tip of thumb
                    if id == 4:
                        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
                    # highlight tip of ptr
                    if id == 8:
                        cv2.circle(img, (cx,cy), 10, (255,0,255), cv2.FILLED)
                    # highlight tip of mid
                    if id == 12:
                       cv2.circle(img, (cx,cy), 10, (255,0,255), cv2.FILLED)    
                    # highlight tip of ring
                    if id == 16:
                        cv2.circle(img, (cx,cy), 10, (255,0,255), cv2.FILLED)    
                    # highlight tip of pinky
                    if id == 20:
                     cv2.circle(img, (cx,cy), 10, (255,0,255), cv2.FILLED)
                if draw:
                    self.mpDraw.draw_landmarks(img, hand, self.mpHands.HAND_CONNECTIONS)
                
            return img



def main():
    cap = cv2.VideoCapture(0)
    a = HandRecognition()

    while True:
        success, img = cap.read()
        img = a.handPosition(img)

        cv2.imshow("Camera", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
