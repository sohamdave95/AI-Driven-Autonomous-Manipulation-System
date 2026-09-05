import cv2
import numpy as np
import torch
from ultralytics import YOLO


model = YOLO("yolov8s-world.pt")
model.set_classes(["toy car", "pen", "earbuds", "hand", "rocket nosecone"])

camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()

    if not ret:
        print("Failed to grab frame")
        break
    
    frame = cv2.flip(frame, 1)

    height, width, _ = frame.shape
    xCenter = width // 2
    yCenter = height // 2
    
    tl = [111, 200]  
    bl = [60, 444]   
    tr = [555, 200]  
    br = [615, 444]  

    # 4 points
    cv2.circle(frame, tuple(tl), 5, (0, 0, 255), -1)
    cv2.circle(frame, tuple(bl), 5, (0, 0, 255), -1)
    cv2.circle(frame, tuple(tr), 5, (0, 0, 255), -1)
    cv2.circle(frame, tuple(br), 5, (0, 0, 255), -1)

    ptLocations = np.array([tl, tr, br, bl], dtype=np.float32)
    transformedPoints = np.array([[0, 0], [640, 0], [640, 480], [0, 480]], dtype=np.float32)

    imgMatrix = cv2.getPerspectiveTransform(ptLocations, transformedPoints)
    transformedImg = cv2.warpPerspective(frame, imgMatrix, (640, 480))

    #simple perspective transform wip.
    #cv2.imshow("webcam", frame)
    

    results = model(transformedImg, conf=0.25)
    annotated_frame = results[0].plot()

    cv2.imshow("bird's eye", transformedImg)
    cv2.imshow("objectdetection", annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


    
camera.release()
cv2.destroyAllWindows()