import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://attendance-system-46645-default-rtdb.firebaseio.com/',
    'storageBucket':'attendance-system-46645.appspot.com'
})

bucket = storage.bucket()
cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

imgBackground = cv2.imread('Res/background.png')

folderModePath = 'Res/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []

modeType = 0
counter = 0
ids = -1
imgStudent = []

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))


# loading encoding file
file = open('EncodeFile.p','rb')
encodingListKnownwithIds = pickle.load(file)
file.close()
encodeListKnown,StudentIds = encodingListKnownwithIds


while True:
    success, img = cap.read()

    imgS = cv2.resize(img,(0,0),None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[162:162+480,55:55+640] = img
    imgBackground[44:44+633,808:808+414] = imgModeList[modeType]

    if faceCurFrame:

        for encodeFace , face_loc in zip(encodeCurFrame,faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)

            matchIdx = np.argmin(faceDis)
            
            if matches[matchIdx]:
                # print("Known Face Detected : ",StudentIds[matchIdx])
                y1 , x2, y2, x1 = face_loc
                y1 , x2, y2, x1 = y1*4 , x2*4, y2*4, x1*4
                bbox = 55 + x1, 162 + y1 , x2 - x1 , y2 - y1

                imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=0)
                ids = StudentIds[matchIdx]

                if counter == 0:
                    counter = 1
                    modeType = 1



            if counter != 0:

                if counter == 1:
                    studentInfo = db.reference(f'Students/{ids}').get()
                    
                    blob = bucket.get_blob(f'img/{ids}.png')
                    array = np.frombuffer(blob.download_as_string(),np.uint8)
                    imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                    dateTimeObject = datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")

                    secondsElapsed = (datetime.now() - dateTimeObject).total_seconds()

                    if secondsElapsed > 20*60*60:
                        ref = db.reference(f'Students/{ids}')
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44:44+633,808:808+414] = imgModeList[modeType]
                        
                if modeType != 3:

                    if 10<counter<20:
                        modeType = 2

                    imgBackground[44:44+633,808:808+414] = imgModeList[modeType]

                    if counter <= 10:

                        cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861,125),cv2.FONT_HERSHEY_COMPLEX, 1 , (255,255,255),1)
                        cv2.putText(imgBackground, str(studentInfo['major']), (1006,550),cv2.FONT_HERSHEY_COMPLEX, 0.5 , (255,255,255),1)
                        cv2.putText(imgBackground, str(ids), (1006,493),cv2.FONT_HERSHEY_COMPLEX, 0.5 , (255,255,255),1)
                        cv2.putText(imgBackground, str(studentInfo['Standing']), (910,625),cv2.FONT_HERSHEY_COMPLEX, 0.6 , (100,100,100),1)
                        cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125,625),cv2.FONT_HERSHEY_COMPLEX, 0.6 , (100,100,100),1)

                        (w,h),_ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                        offset = (414-w)//2
                        cv2.putText(imgBackground, str(studentInfo['name']), (808+offset,445),cv2.FONT_HERSHEY_COMPLEX, 1 , (50,50,50),1)
                        imgBackground[175:175+216,909:909+216] = imgStudent

                    counter += 1

                    if counter>= 20:
                        counter = 0
                        modeType = 0
                        studentInfo = [] 
                        imgStudent = []
                        imgBackground[44:44+633,808:808+414] = imgModeList[modeType]
    
    else:
        modeType = 0
        counter = 0

         
    
    cv2.imshow("Face Attendance",imgBackground)
    cv2.waitKey(1)

