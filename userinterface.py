import wx
from facial import compare_faces
import cv2 as cv
import face_recognition
import time
class MyFrame(wx.Frame):  
      
    def __init__(self):
        super().__init__(parent=None, title='Household AI')
        panel = wx.Panel(self)
        
        image_file = 'C://Users//anujv//Household-AI//door.jpg'
        image = wx.Image(image_file, wx.BITMAP_TYPE_ANY)
        bmp = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(image))
        login = wx.Button(panel, label='Login', pos=(5, 230))
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
        images= ["Household-AI/Anuj.jpg"]
        
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