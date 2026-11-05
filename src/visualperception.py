import cv2
import numpy as np
from ultralytics import YOLO
import serial
import time
import threading


model = YOLO("yolov8s-world.pt")
model.set_classes(["toy car", "pen"])

camera = cv2.VideoCapture(0)
workspaceWidth = 38.0 # in cm
workspaceHeight = 22.0 # in cm
scaledY = 38.0/640
scaledX = 22.0/480
xOffset = 1.0
yOffset = 34.0
referenceFrameOffset = 17.0

esp32 = serial.Serial('COM3', 115200, timeout=1)


latestTransformedImg = None
annotatedFrame = None
lastSendTime = 0
sendDelay = 6
dataLock = threading.Lock()

def yolo_worker_thread():
    
    global latestTransformedImg, annotatedFrame, lastSendTime
    
    while True:
        if latestTransformedImg is None:
            time.sleep(0.01)
            continue
            
        
        with dataLock:
            imgToProcess = latestTransformedImg.copy()
            
        
        results = model(imgToProcess, conf=0.1, verbose=False)
        
        if results and len(results) > 0:
            
            tempAnnotated = results[0].plot()
            
            if len(results[0].boxes) > 0:
                
                xmin, ymin, xmax, ymax = results[0].boxes.xyxy[0].tolist()
                center_u = (xmin + xmax) / 2
                center_v = (ymin + ymax) / 2
                real_y = (yOffset - center_u * scaledY) - referenceFrameOffset
                real_x = center_v * scaledX - xOffset
                
                text = f" X: {real_x:.1f} Y: {real_y:.1f}"
                cv2.putText(tempAnnotated, text, (int(xmin), max(int(ymin) - 10, 20)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                
                currentTime = time.time()
                if currentTime - lastSendTime > sendDelay:
                    serialMsg = f"{real_x:.2f}, {real_y:.2f}\n"
                    esp32.write(serialMsg.encode('utf-8'))
                    print(f"Sent coordinates: {serialMsg.strip()}")
                    lastSendTime = currentTime
            
            
            with dataLock:
                annotatedFrame = tempAnnotated


threading.Thread(target=yolo_worker_thread, daemon=True).start()

while True:
    ret, frame = camera.read()
    if not ret:
        print("Failed to grab frame")
        break
    
    frame = cv2.flip(frame, 1)
    
    tl = [111, 200]  
    bl = [60, 444]   
    tr = [555, 200]  
    br = [615, 444]  

    cv2.circle(frame, tuple(tl), 5, (0, 0, 255), -1)
    cv2.circle(frame, tuple(bl), 5, (0, 0, 255), -1)
    cv2.circle(frame, tuple(tr), 5, (0, 0, 255), -1)
    cv2.circle(frame, tuple(br), 5, (0, 0, 255), -1)

    ptLocations = np.array([tl, tr, br, bl], dtype=np.float32)
    transformedPoints = np.array([[0, 0], [640, 0], [640, 480], [0, 480]], dtype=np.float32)

    imgMatrix = cv2.getPerspectiveTransform(ptLocations, transformedPoints)
    transformedImg = cv2.warpPerspective(frame, imgMatrix, (640, 480))

    
    with dataLock:
        latestTransformedImg = transformedImg

    
    with dataLock:
        if annotatedFrame is not None:
            cv2.imshow("object detection", annotatedFrame)
        else:
            # if the proper frame has not been processed yet, to prevent screen freezes.
            cv2.imshow("object detection", transformedImg)
            
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
