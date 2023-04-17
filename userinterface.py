import wx
from facial import compare_faces
import cv2 as cv
import face_recognition
class MyFrame(wx.Frame):  
      
    def __init__(self):
        super().__init__(parent=None, title='Household AI')
        panel = wx.Panel(self)
        login = wx.Button(panel, label='Login', pos=(5, 55))
        login.Bind(wx.EVT_BUTTON, self.face)
        self.Show()
       
    def gestures(self):
        super().__init__(parent=None, title='Gestures')
        gestures = wx.Panel(self)
        logout = wx.Button(gestures, label='Logout', pos=(5, 55))
        logout.Bind(wx.EVT_BUTTON, self.logout)
        self.Show()
    def logout(self,event):
        self.Hide()
        self.__init__()
    def face(self,event):
        vid = cv.VideoCapture(0)
        wx.MessageBox('Press space to take picture', 'Household AI')
        while(True):
    
            ret, img = vid.read()
  
#     # Display the resulting frame
            cv.imshow('frame', img)
            if cv.waitKey(1) & 0xFF == ord(' '):
                break
        images= ["C:\\Users\\anujv\\OneDrive\\Pictures\\Camera Roll\\Anuj.jpg"]
        
        if(any(compare_faces(images,img))):
            wx.MessageBox('login succeeded', 'Household AI')
            cv.destroyAllWindows()
            self.Hide()
            self.gestures()
        else:
            wx.MessageBox('identity not authorized', 'Error',wx.ICON_ERROR)
            cv.destroyAllWindows()
            



if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()