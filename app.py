from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
from fastapi.staticfiles import StaticFiles

import random
from model import Patient, DISEASES

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# Initialize a demo VAIP patient
# to be replaced by generated VAIP patient
p = Patient()


def generate_random_range(x, y):
    x_random = random.randint(x, int(y/2))
    y_random = random.randint(x_random+1, y)
    return [x_random, y_random]



class ChatRequest(BaseModel):
    messages: list
    patient_info: dict
    disease: str



@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/try")
async def try_it(request: Request):
    return templates.TemplateResponse("try.html", {"request": request})




@app.post("/generate")
async def generate():
    global p
    disease = DISEASES[random.randint(0, len(DISEASES)-1)]["disease"]
    # disease = "Pneumonia"
    print(disease)
    # Generate a demo VAIP patient
    p = Patient(disease=disease)

    # Generate a patient info
    patient = p.get_info()
    try:

        symptoms = p.get_symptoms()
        hotspots = p.get_hotspots()

        i = 2
        for hotspot in hotspots:
            hotspot['id'] = "hotspot-"+str(i)
            i += 1

        example_patient = {
            "chief-complaint": "I've been experiencing a persistent cough accompanied by difficulty breathing, fatigue, and chest pain. The cough feels deep and phlegm-filled, making it hard for me to get a good night's sleep. I've also noticed a high fever, chills, and a general feeling of weakness. Overall, I'm concerned about my respiratory symptoms and their impact on my daily activities."
        }
        response = {
            "symptoms": symptoms,
            "disease": disease,
            "hotspots": hotspots,
            "patient": patient
        }
        return response

    except Exception as e:
        response = {
            "error": True,
            "disease": "disease",
            "message": str(e),
            "patient": patient
        }
        return response


@app.post("/chat")
async def chat(request_data: ChatRequest):
    messages = []
    try:

        messages = list(request_data.messages)
        patient_info = dict(request_data.patient_info)
        disease = request_data.disease
        p.disease = disease
        p.patient_info = patient_info
        p.update_chat_prompt()
        response_messages = p.chat(messages)

        response = {
            "success": True,
            "response": response_messages,
            "answer": response_messages[-1]["content"],
        }
        return response
    except Exception as e:
        errorMessage = str(e)
        errorMessage = "Patient not exist yet" if errorMessage == "'str' object has no attribute 'chat'" else errorMessage
        print('Error', e)

        messages.append({
            "role": "assistant", "content": "i couldn't get you, check console.."
        })
        response = {
            "error": True,
            "message": errorMessage,
            "response": messages,
            "answer": "server error says \n"+errorMessage,
        }
        return response


    
    
    
@app.get("/diseases")
async def diseases():
    from model import DISEASES

    return DISEASES



# Run the FastAPI app using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

