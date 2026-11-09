import llmapi
import serial
import time
import visualperception

esp32 = serial.Serial('COM3', 115200, timeout=1)
time.sleep(2)


while True:
    userInput = input("\nSay what you want the arm to do or type q to quit: ")
    if userInput.lower() == 'q':
        break

   
    try:
        results = llmapi.generateInstructions(userInput)
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        continue

    
    target_obj = results.get("target_object")
    if target_obj:
        visualperception.set_yolo_classes([target_obj])
        time.sleep(1.0) 
    
    plan = results.get("plan", [])

    for step in plan:
        cmd = step.get("command", "").lower()
        x = step.get("x", 0.0)
        y = step.get("y", 0.0)
        z = step.get("z", 0.0)

        if cmd == "move":
            serialMsg = f"{x},{y},{z},{cmd}\n"
        else:
            serialMsg = f"{cmd}\n"

        print(f"Sending to ESP32 -> {serialMsg.strip()}")
        esp32.write(serialMsg.encode('utf-8'))
        
        time.sleep(2.0)


