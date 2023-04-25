import pyautogui


class DesktopControl:
    def get_mouse_position(self):
        return pyautogui.position()

    def move_mouse(self, x, y):
        pyautogui.moveTo(x, y, _pause=False)

    def move_mouse_rel(self, x_incr, y_incr):
        pyautogui.moveRel(x_incr, y_incr, _pause=False)

    def left_click(self):
        x, y = pyautogui.position()
        pyautogui.click(x, y, _pause=False)

    def hold_left_click(self):
        pyautogui.mouseDown(_pause=False)

    def release_left_click(self):
        pyautogui.mouseUp(_pause=False)
