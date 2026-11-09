import cv2
import numpy as np
from ultralytics import YOLO
import time
import threading

#NOTES: 
# model.set_classes's parameters should be adjustable via the genai file.
#leave solely cv stuff left within this file, and all the main sending stuff handled via genai file.
# 

model = YOLO("yolov8s-world.pt")
camera = cv2.VideoCapture(0)
workspaceWidth = 38.0 # in cm
workspaceHeight = 22.0 # in cm
scaledY = 38.0/640
scaledX = 22.0/480
xOffset = 1.0
yOffset = 34.0
referenceFrameOffset = 17.0
grabHeightOffset = 3

latest_real_x = 0.0
latest_real_y = 0.0
latest_real_z = 0.0
current_detected_object = ""

latestTransformedImg = None
annotatedFrame = None
dataLock = threading.Lock()

def set_yolo_classes(class_list):
    model.set_classes(class_list)



def start_camera_display():
    global latestTransformedImg, annotatedFrame
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
                cv2.imshow("object detection", transformedImg)
                
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

threading.Thread(target=start_camera_display, daemon=True).start()

def yolo_worker_thread():
    global latestTransformedImg, annotatedFrame, latest_real_x, latest_real_y, latest_real_z, current_detected_object
    
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
                box = results[0].boxes[0]
                xmin, ymin, xmax, ymax = box.xyxy[0].tolist()
                cls_id = int(box.cls[0].item())
                obj_name = model.names[cls_id] if cls_id in model.names else "unknown"
                
                center_u = (xmin + xmax) / 2
                center_v = (ymin + ymax) / 2
                real_y = (yOffset - center_u * scaledY) - referenceFrameOffset
                real_x = center_v * scaledX - xOffset
                real_z = 0  
                
                with dataLock:
                    latest_real_x = real_x
                    latest_real_y = real_y
                    latest_real_z = real_z
                    current_detected_object = obj_name

                text = f"{obj_name} X: {real_x:.1f} Y: {real_y:.1f}"
                cv2.putText(tempAnnotated, text, (int(xmin), max(int(ymin) - 10, 20)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            with dataLock:
                annotatedFrame = tempAnnotated


threading.Thread(target=yolo_worker_thread, daemon=True).start()