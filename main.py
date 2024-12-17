# main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator  # Use @validator for Pydantic 1.x
from fastapi.exceptions import RequestValidationError
from app.operations import *# Ensure correct import path
import uvicorn
import logging
import requests
import json
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# API Endpoint and API Key
API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = os.getenv("API_KEY")  


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Setup templates directory
templates = Jinja2Templates(directory="templates")
def call_groq_function(prompt, model="llama3-8b-8192"):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "functions":[ 
        {
            "name": "add",
            "description": "Add two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number."},
                    "b": {"type": "number", "description": "The second number."}
                },
                "required": ["a", "b"]
            },
        },
        {
            "name": "subtract",
            "description": "Subtract two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number."},
                    "b": {"type": "number", "description": "The second number."}
                },
                "required": ["a", "b"]
            },
        },
        {
            "name": "multiply",
            "description": "Multiply two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number."},
                    "b": {"type": "number", "description": "The second number."}
                },
                "required": ["a", "b"]
            },
        },
        {
            "name": "divide",
            "description": "Divide two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number."},
                    "b": {"type": "number", "description": "The second number."}
                },
                "required": ["a", "b"]
            },
        },
        {
            "name": "Power",
            "description": "Power two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number."},
                    "b": {"type": "number", "description": "The second number."}
                },
                "required": ["a", "b"]
            },
        },
        {
            "name": "Modulus",
            "description": "Modulus two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number."},
                    "b": {"type": "number", "description": "The second number."}
                },
                "required": ["a", "b"]
            },
        }
    ],

        "function_call": "auto",
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Check if the model called a function
        if "function_call" in data["choices"][0]["message"]:
            function_name = data["choices"][0]["message"]["function_call"]["name"]
            arguments = json.loads(data["choices"][0]["message"]["function_call"]["arguments"])
            return function_name, arguments

        return None, None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None, None


# Pydantic model for request data
class OperationRequest(BaseModel):
    a: float = Field(..., description="The first number")
    b: float = Field(..., description="The second number")

    @field_validator('a', 'b')  # Correct decorator for Pydantic 1.x
    def validate_numbers(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError('Both a and b must be numbers.')
        return value

# Pydantic model for successful response
class OperationResponse(BaseModel):
    result: float = Field(..., description="The result of the operation")

# Pydantic model for error response
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

# Custom Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extracting error messages
    error_messages = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    logger.error(f"ValidationError on {request.url.path}: {error_messages}")
    return JSONResponse(
        status_code=400,
        content={"error": error_messages},
    )

@app.get("/")
async def read_root(request: Request):
    """
    Serve the index.html template.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/add", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def add_route(operation: OperationRequest):
    """
    Add two numbers.
    """
    try:
        prompt = gen_add_prompt(operation.a, operation.b)
        ignore, args = call_groq_function(prompt)
        if ignore and args:
            result = add(args["a"], args["b"])
        else:
            logger.error(f"add Operation Error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Add Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/subtract", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def subtract_route(operation: OperationRequest):
    """
    Subtract two numbers.
    """
    try:
        prompt = gen_substraction_prompt(operation.a, operation.b)
        ignore, args = call_groq_function(prompt)
        if ignore and args:
            result = subtract (args["a"], args["b"])
        else:
            logger.error(f"Subtract Operation Error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Subtract Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/multiply", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def multiply_route(operation: OperationRequest):
    """
    Multiply two numbers.
    """
    try:
        prompt = gen_multiply_prompt(operation.a, operation.b)
        ignore, args = call_groq_function(prompt)
        if ignore and args:
            result = multiply (args["a"], args["b"])
        else:
            logger.error(f"Multiply Operation Error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Multiply Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/divide", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def divide_route(operation: OperationRequest):
    """
    Divide two numbers.
    """
    try:
        prompt = gen_division_prompt(operation.a, operation.b)
        ignore, args = call_groq_function(prompt)
        if ignore and args:
            result = divide (args["a"], args["b"])
        else:
            logger.error(f"Opperation error")
            raise HTTPException(status_code=400, detail=str(e))
        return OperationResponse(result=result)
    except ValueError as e:
        logger.error(f"Divide Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Divide Operation Internal Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/modulus", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def modulus_route(operation: OperationRequest):
    """
    modulus two numbers.
    """
    try:
        prompt = gen_modulus_prompt(operation.a, operation.b)
        ignore, args = call_groq_function(prompt)
        if ignore and args:
            result = modulus (args["a"], args["b"])
        else:
            logger.error(f"Mod Operation Error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        return OperationResponse(result=result)
    except ValueError as e:
        logger.error(f"Mod Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Mod Operation Internal Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/power", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def power_route(operation: OperationRequest):
    """
    Take the power of two numbers.
    """
    try:
        prompt = gen_power_prompt(operation.a, operation.b)
        ignore, args = call_groq_function(prompt)
        if ignore and args:
            result = power (args["a"], args["b"])
        else:
            logger.error(f"Power Operation Error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Power Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

