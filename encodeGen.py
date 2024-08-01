import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://attendance-system-46645-default-rtdb.firebaseio.com/',
    'storageBucket':'attendance-system-46645.appspot.com'
})

imgBackground = cv2.imread('Res/background.png')

folderPath = 'img'
PathList = os.listdir(folderPath)
imgList = []
StudentIds = []

for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    StudId = os.path.splitext(path)[0]
    StudentIds.append(StudId)

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


def findEncoding(imagesList):
    encodeList = []

    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]

        encodeList.append(encode)

    return encodeList

print("Encoding Started...")
encodeListKnown = findEncoding(imgList)
encodingListKnownwithIds = [encodeListKnown,StudentIds]
print("Encoding Completed")


file = open('EncodeFile.p','wb')
pickle.dump(encodingListKnownwithIds,file)
file.close()
print("File Saved..")



