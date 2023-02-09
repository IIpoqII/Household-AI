import cv2 as cv
import face_recognition
image = face_recognition.load_image_file("C:\\Users\\anujv\\Downloads\\Anuj.jpg")
test = face_recognition.load_image_file("C:\\Users\\anujv\\Downloads\\stock.jpg")
face_encodings = face_recognition.face_encodings(image)[0]
test_encoding = face_recognition.face_encodings(test)[0]
print(face_recognition.face_distance([face_encodings],test_encoding))
print(face_recognition.compare_faces([face_encodings],test_encoding))
