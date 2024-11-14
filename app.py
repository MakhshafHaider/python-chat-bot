import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.oauth2 import service_account
from flask import Flask, request, jsonify, render_template

# Load environment variables
load_dotenv()

# Path to your service account key file
credentials_path = "focus-cairn-435505-b5-16553483d876.json"

# Load the service account credentials
credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Access the environment variable for the API key
api_key = os.getenv("API_KEY")

# Configure the Google Generative AI
genai.configure(api_key=api_key, credentials=credentials)

# Create the model configuration
generation_config = {
    "temperature": 1.9,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Initialize chat history globally
chat_history = [
    {
        "role": "user",
        "parts": ["hy!\n\n"],
    },
    {
        "role": "model",
        "parts": ["Hello! How can I help you today? \n"],
    },
]

# Initialize Flask app
app = Flask(__name__)

# Route to render the chat page (HTML frontend)
@app.route("/")
def index():
    return render_template("app.html")  # Render your chat page

# Route to handle the AI interaction and return the response
@app.route("/send_message", methods=["POST"])
def send_message():
    global chat_history

    user_input = request.json.get('message')

    # Append user's message to the chat history
    chat_history.append({
        "role": "user",
        "parts": [user_input]
    })

    # Send the updated history to the AI model
    chat_session = model.start_chat(history=chat_history)

    # Send the user's message to the AI model and get the response
    response = chat_session.send_message(user_input)

    # Append AI's response to the chat history
    chat_history.append({
        "role": "model",
        "parts": [response.text]
    })

    # Return the response back to the frontend
    return jsonify({"response": response.text})

# Route to handle the final cost estimation
@app.route("/cost_estimation", methods=["POST"])
def cost_estimation():
    # Generate cost estimation
    cost_estimation_prompt = """
    Please create a detailed cost and time estimation for the services required. Before you start, list any assumptions you are making about the project.
    Then, structure the response in a table format with the following columns:

    1. Task
    2. Time (in hours)
    3. Hourly Rate (in dollars, with a maximum rate of $30)
    4. Total Cost (calculated as Time * Hourly Rate)

    Make sure the table is neatly formatted with borders and clear headings, using lines to separate the rows and columns. Present the table in a grid format with clear alignment.
    """

    # Send the prompt to the AI model
    response = model.start_chat(history=chat_history).send_message(cost_estimation_prompt)

    # Append AI's response to the chat history
    chat_history.append({
        "role": "model",
        "parts": [response.text]
    })

    # Return the cost estimation response
    return jsonify({"response": response.text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
