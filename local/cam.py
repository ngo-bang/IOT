import cv2
import requests
HOUSEKEY="12345"
def send_to_server(image_data):
    url = 'http://13.213.40.27/requestcamera'
    # url = 'http://127.0.0.1:8000/requestcamera'
    files = {'image': ('image.jpg', image_data)}
    form = {'housekey': HOUSEKEY}
    resp = requests.post(url, data=form,files=files)
    print(resp.json())
    print(resp.status_code)
# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# To capture video from webcam. 
IP = "http://192.168.0.2:4747/video";
cap = cv2.VideoCapture(IP)
# To use a video file as input 
# cap = cv2.VideoCapture('filename.mp4')
d=0
while True:
    # Read the frame
    _, img = cap.read()
    d+=1
    
    if d%20 ==0:
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect the faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
       
        if len(faces)>0:
            # cv2.putText("khuôn mặt đang được xác thưc")
            _, img_encoded = cv2.imencode('.jpg', img)
            img_bytes = img_encoded.tobytes()
            print(type(img_bytes))
            send_to_server(img_bytes)
        
        # for (x, y, w, h) in faces:
        #     cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Display
    # cv2.imshow('img', img)

    # Stop if escape key is pressed
    # k = cv2.waitKey(30) & 0xff
    # if k==27:
    #     break
        
# Release the VideoCapture object
cap.release()