import cv2
import face_recognition
import pickle
import os
from supabase import create_client, Client


SUPABASE_URL = "url"
SUPABASE_KEY = "api key"
storage_bucket ="student-images"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentIds = []
for path in pathList:
    img_path = os.path.join(folderPath, path)
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentIds.append(os.path.splitext(path)[0])


    with open(img_path, "rb") as f:
        file_bytes = f.read()
        supabase.storage.from_(storage_bucket).upload(path, file_bytes)
        print(f"Uploaded {path} to Supabase")


   # print(path)
  #  print(os.path.splitext(path)[0])
print(studentIds)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList
print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

file = open("Encodefile.p",'wb')
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File Complete Saved")
