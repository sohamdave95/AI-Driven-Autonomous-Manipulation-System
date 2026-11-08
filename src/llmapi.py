import visualperception
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("apiKey"))

def generateInstructions(user_prompt: str) -> dict:
    with visualperception.dataLock:
        obj_name = visualperception.current_detected_object
        obj_x = visualperception.latest_real_x
        obj_y = visualperception.latest_real_y
        obj_z = visualperception.latest_real_z

    system_instruction = """
    You are the cognitive task planner for a 4DOF robotic arm. 
    Available hardware commands: 'move' (requires x,y,z coordinates in cm), 'open', 'close', 'home'.
    
    You must output a valid JSON object containing:
    1. "target_object": A string naming the specific object the user wants to find or interact with (used to update the YOLO-World vision model).
    2. "plan": A list of command steps to execute.
    """

    vision_context = {
        "current_detected_object": obj_name,
        "coordinates_cm": {"x": obj_x, "y": obj_y, "z": obj_z}
    }

    user_payload = f"User Request: '{user_prompt}'\nLive Camera Feed Data: {json.dumps(vision_context)}"

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"{system_instruction}\n\n{user_payload}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,  # low temp for more realisitic answers
        ),
    )

    plan_data = json.loads(response.text)
    return plan_data