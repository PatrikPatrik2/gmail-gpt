import openai
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

function_descriptions = [
    {
        "name": "extract_info_from_email",
        "description": "categorise & extract key info from an email, such as use case, company name, contact details, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "companyName": {
                    "type": "string",
                    "description": "the name of the company from which the mail was sent to, the company requesting the sales or service. The company name should not be Uponor"
                },                        
                "priority": {
                    "type": "string",
                    "description": "Try to give a priority score to this email based on how likely this email will leads to a good business opportunity, from 0 to 10; 10 most important"
                },
                "category": {
                    "type": "string",
                    "description": "Try to categorise this email into categories like those: 1. Sales 2. customer support; 3. consulting; 4. Technichal support; etc."
                },
                "product": {
                    "type": "string",
                    "description": "Try to identify which product the client is interested in, if any"
                },
                "amount":{
                    "type": "string",
                    "description": "Try to identify the amount of products the client wants to purchase, if any"
                },
                "nextStep":{
                    "type": "string",
                    "description": "What is the suggested next step to move this forward?"
                },
                "namesender":{
                    "type": "string",
                    "description": "What is the name of the individual that sent the mail?"
                },
                "replymail":{
                    "type": "string",
                    "description": "A friendly and personal response to the mail from the company Uponors technical service department?"
                },
                "replymailadress":{
                    "type": "string",
                    "description": "the email of the person sending the mail. This email is not uponordummyacount@gmail.com"
                },
                "technichal_question":{
                    "type": "string",
                    "description": "if the mail contains questions regarding technichal support, summarize the technical support question in a neutral way, this will be used for a vector search"
                },
                "sentiment":{
                    "type": "string",
                    "description": "Rate the sentiment in the mail on a scale 1 to 10, where 1 is very negative and 10 is very positive"
                }
            },
            "required": ["companyName", "amount", "product", "priority", "category", "nextStep", "replymail", "namesender" , "replymailadress", "sentiment"]
        }
    }
]

class Email(BaseModel):
    from_email: str
    content: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/")
def analyse_email(email: Email):
    content = email.content
    query = f"Please extract key information from this email and prepare an answer: {content} "

    messages = [{"role": "user", "content": query}]

    response = openai.ChatCompletion.create(
        #model="gpt-3.5-turbo-0613",
        model="gpt-4",
        messages=messages,
        functions = function_descriptions,
        function_call="auto"
    )

    arguments = response.choices[0]["message"]["function_call"]["arguments"]
    companyName = eval(arguments).get("companyName")
    priority = eval(arguments).get("priority")
    product = eval(arguments).get("product")
    amount = eval(arguments).get("amount")
    category = eval(arguments).get("category")
    nextStep = eval(arguments).get("nextStep")
    namesender = eval(arguments).get("namesender")
    replymail = eval(arguments).get("replymail")
    replymailadress = eval(arguments).get("replymailadress")
    sentiment = eval(arguments).get("sentiment")
    technichal_question = eval(arguments).get("technichal_question")


    return {
        "companyName": companyName,
        "product": product,
        "amount": amount,
        "priority": priority,
        "category": category,
        "nextStep": nextStep,
        "NameSender" : namesender,
        "ReplyMail" : replymail,
        "ReplyMailAdress" : replymailadress,
        "Technichal_question" : technichal_question,
        "Sentiment" : sentiment
    }
