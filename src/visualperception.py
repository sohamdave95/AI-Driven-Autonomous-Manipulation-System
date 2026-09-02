import cv2
import numpy as np
import torch
from transformers import OwlViTProcessor, OwlViTForObjectDetection
from PIL import Image


processor = OwlViTProcessor.from_pretrained("google/owlvit-base-patch32")
model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch32")
model.eval()

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

    texts = ["toy car", "Hot Wheels car"]

    
    image_rgb = cv2.cvtColor(transformedImg, cv2.COLOR_BGR2RGB) #learned this the hard way, converts color channels from bgr as in cv2 to rgb for the huggingface model.
    pil_image = Image.fromarray(image_rgb)

    
    inputs = processor(text=texts, images=pil_image, return_tensors="pt") #feed images into model as a tensor
    with torch.no_grad():
        outputs = model(**inputs)

    
    target_sizes = torch.tensor([pil_image.size[::-1]])
    results = processor.image_processor.post_process_object_detection(outputs, threshold=0.15, target_sizes=target_sizes)[0]
    for box, score, label in zip(results["boxes"], results["scores"], results["labels"]):
        box = [int(i) for i in box.tolist()]
        x1, y1, x2, y2 = box

        u = int((x1 + x2) / 2)
        v = int((y1 + y2) / 2)

        cv2.rectangle(transformedImg, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(transformedImg, (u, v), 5, (0, 0, 255), -1)

    
    





    #simple perspective transform wip.
    cv2.imshow("webcam", frame)
    cv2.imshow("bird's eye", transformedImg)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


    
camera.release()
cv2.destroyAllWindows()