import cv2
import math
import HandTracker as ht


class RotateHandGesture():
    def __init__(self):
        self.hand_tracker = ht.HandRecognition()

    def draw_gesture(self, img, x1, y1, x2, y2, x3, y3):
        cv2.line(img, (x1, y1), (x2, y2), (255, 127, 0), 3)
        cv2.line(img, (x2, y2), (x3, y3), (255, 127, 0), 3)

    def detect(self, img, lmList, lower_bound=0.45, upper_bound=0.75):
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        x3, y3 = lmList[12][1], lmList[12][2]
        # cv2.line(img, (x1, y1), (x2, y2), (255, 127, 0), 3)
        # cv2.line(img, (x2, y2), (x3, y3), (255, 127, 0), 3)
        len1 = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        len2 = math.sqrt(math.pow(x2 - x3, 2) + math.pow(y2 - y3, 2))
        ratio = 0
        if len1 != 0:
            ratio = round(len2 / len1, 2)
        print(ratio)
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
            angle = math.atan((m1 - m2) / (1 + (m1 * m2)))
            angle = round(math.degrees(angle))
        return angle

    def execute(self, capture, img, lmList, threshold=True):
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[12][1], lmList[12][2]
        while threshold:
            success, img = capture.read()
            img = ht.track_hand(img)
            lmList = ht.get_landmarks_positions(img)

            x3, y3 = lmList[12][1], lmList[12][2]
            angle = self.get_angle(x1, y1, x2, y2, x3, y3)
            increment = round(angle/5)
            if increment <= -2 or increment >= 2:
                self.volume_control(img)

            threshold = self.detect(img, lmList)
            cv2.imshow("Camera", img)
            cv2.waitKey(1)

    def volume_control(self, img):
        cv2.rectangle(img, (10, 10), (50, 20), (255, 127, 0), 2, cv2.FILLED)


def main():
    cam_width, cam_height = 1280, 720

    capture = cv2.VideoCapture(0)
    capture.set(3, cam_width)
    capture.set(4, cam_height)

    while True:
        success, img = capture.read()
        img = ht.track_hand(img)
        lmList = ht.get_landmarks_positions(img)
        if RotateHandGesture().detect(lmList):
            RotateHandGesture().execute(capture, img, lmList)

        cv2.imshow("Camera", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
