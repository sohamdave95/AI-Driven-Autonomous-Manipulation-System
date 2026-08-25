import cv2
import numpy as np

camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()


    frame = cv2.flip(frame, 1)

    height, width, _ = frame.shape
    xCenter = width // 2
    yCenter = height // 2
    
    tl = [111, 200]  # Left side
    bl = [60, 444]   # Left side
    tr = [555, 200]  # Right side
    br = [615, 444]  # Right side

    # 2. Draw AFTER the flip
    cv2.circle(frame, tuple(tl), 5, (0, 0, 255), -1)
    cv2.circle(frame, tuple(bl), 5, (0, 0, 255), -1)
    cv2.circle(frame, tuple(tr), 5, (0, 0, 255), -1)
    cv2.circle(frame, tuple(br), 5, (0, 0, 255), -1)

    ptLocations = [tl, bl, tr, br]
    transformedPoints = [[0,0], [0,480], [640, 0], [640, 480]]

    imgMatrix = cv2.getPerspectiveTransform(ptLocations, transformedPoints)

    #simple perspective transform wip.
    cv2.imshow("webcam", frame)

    if not ret:
        print("Failed to grab frame")
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
camera.release()
cv2.destroyAllWindows()