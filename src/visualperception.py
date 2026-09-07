import cv2
import numpy as np
from ultralytics import YOLO


model = YOLO("yolov8s-world.pt")
model.set_classes(["toy car", "pen", "earbuds", "hand", "rocket nosecone"])

camera = cv2.VideoCapture(0)
workspaceWidth = 38.0 #in cm
workspaceHeight = 22.0 #in cm
scaledY = 38.0/640
scaledX = 22.0/480
xOffset = 1
yOffset = 34.0


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


    

    results = model(transformedImg, conf=0.15)
    annotated_frame = results[0].plot()

    for box in results[0].boxes:
        xmin, ymin, xmax, ymax = box.xyxy[0].tolist()
        center_u = (xmin + xmax) / 2
        center_v = (ymin + ymax) / 2
        real_y = yOffset - center_u * scaledY 
        real_x = center_v * scaledX - xOffset
        text = f"X: {real_x:.1f} Y: {real_y:.1f}"
        cv2.putText(annotated_frame, text, (int(xmin), max(int(ymin) - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    #cv2.imshow("bird's eye", transformedImg)
    cv2.imshow("object detection", annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


    
camera.release()
cv2.destroyAllWindows()