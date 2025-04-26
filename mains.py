import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
from supabase import create_client, Client
from datetime import datetime, timezone

SUPABASE_URL = "url"
SUPABASE_KEY = "api key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')


folderModePath = 'Resources/Modes'
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in os.listdir(folderModePath)]


print("Loading Encode File ...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []
studentData = {}

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = [v * 4 for v in faceLoc]
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = str(studentIds[matchIndex])

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)

                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                print(f"Looking for student with id: {id}")
                studentInfo = supabase.table("students").select("*").eq("id", id).single().execute()
                studentData = studentInfo.data
                print("Student Data:", studentData)


                try:
                    res = supabase.storage.from_('student-images').download(f'{id}.png')
                    array = np.frombuffer(res, np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                except Exception as e:
                    print(f"Image load error for {id}: {e}")
                    imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)


                if studentData.get('last_attendance_time'):
                    last_time = datetime.fromisoformat(studentData['last_attendance_time'])
                    current_time = datetime.now(timezone.utc)
                    secondsElapsed = (current_time - last_time).total_seconds()
                else:
                    secondsElapsed = 9999

                print(f"Time since last attendance: {int(secondsElapsed)} sec")

                if secondsElapsed > 30:
                    studentData['total_attendance'] += 1
                    current_time = datetime.now(timezone.utc)
                    supabase.table("students").update({
                        "total_attendance": studentData['total_attendance'],
                        "last_attendance_time": current_time.isoformat()
                    }).eq("id", id).execute()
                    print("Attendance updated.")
                else:
                    print("Recently checked in, skipping update.")
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentData['total_attendance']), (861, 125),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(imgBackground, str(studentData.get('course')), (1006, 550),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentData['id']), (1006, 493),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentData.get('batch',)), (910, 625),
                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentData['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentData['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 2)

                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentData = {}
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)