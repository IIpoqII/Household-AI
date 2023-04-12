import cv2 as cv
import face_recognition
def compare_faces(images,test):
    face_encodings = []
    for i in images:
        image = face_recognition.load_image_file(i)
        face_encodings.append(face_recognition.face_encodings(image)[0])
    
    
    test_encoding = face_recognition.face_encodings(test)[0]
    print(face_recognition.face_distance(face_encodings,test_encoding))
    return face_recognition.compare_faces(face_encodings,test_encoding)
# images= ["C:\\Users\\anujv\\OneDrive\\Pictures\\Camera Roll\\Anuj.jpg"]


# vid = cv.VideoCapture(0)
# while(True):
    
#     ret, img = vid.read()
  
# #     # Display the resulting frame
#     cv.imshow('frame', img)
#     if cv.waitKey(1) & 0xFF == ord('q'):
#         break
# print(compare_faces(images,img))

  


