import wx
from facial import compare_faces
import cv2 as cv
import face_recognition
class MyFrame(wx.Frame):    
    def __init__(self):
        super().__init__(parent=None, title='Household AI')
        panel = wx.Panel(self)
        my_btn = wx.Button(panel, label='Login', pos=(5, 55))
        my_btn.Bind(wx.EVT_BUTTON, self.face)
        self.Show()
    def face(self,event):
        vid = cv.VideoCapture(0)
        while(True):
    
            ret, img = vid.read()
  
#     # Display the resulting frame
            cv.imshow('frame', img)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        images= ["C:\\Users\\anujv\\OneDrive\\Pictures\\Camera Roll\\Anuj.jpg"]
        
        if(any(compare_faces(images,img))):
            wx.MessageBox('login succeeded', 'Household AI')    
        else:
            wx.MessageBox('identity not authorized', 'Error',wx.ICON_ERROR)
            



if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()