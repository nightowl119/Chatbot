from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import csv

app = Flask(__name__)
CORS(app)

def solve_math_problem(question):
    expression = re.findall(r'[\d\.\+\-\*\/\(\) ]+', question)
    if expression:
        expression = ''.join(expression)  
        result = eval(expression)
        return f"The answer is {result}."

# Load model and tokenizer once at the start
model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def encode_text(text):
    """Encodes text into embeddings."""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.detach().numpy()

# Load and encode each sentence from the paragraph
with open('para.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')

with open("para.txt", "r", encoding="utf-8") as file:
    paragraph = file.read()

# Split paragraph into sentences, encode them, and store embeddings
sentences = [sent.strip() for sent in re.split(r'(?<=[.!?]) +', paragraph) if sent]  # More robust splitting
sentence_embeddings = [encode_text(sentence) for sentence in sentences]

def convert_links(text):
    """Converts URLs in text to clickable links."""
    # Regex to find URLs
    url_pattern = r'(https?://\S+)'
    return re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)

def get_answer(question):
    """Retrieves the best answer based on similarity to the question."""
    greetings = ['hi', 'hey', 'hello', 'howdy']
    thanks_responses = ['thank you', 'thanks', 'appreciate it']
    question_lower = question.lower()

    # Check for common greetings or thanks responses
    if any(greeting in question_lower for greeting in greetings):
        return "Hello! How can I assist you today?"
    if any(thanks in question_lower for thanks in thanks_responses):
        return "You're welcome! Ask away if there's more you'd like to know."

    # Check if the question contains a math problem
    if re.search(r'\d', question):  # Check if there's a digit in the question
        return solve_math_problem(question)

    # Calculate question embedding
    question_embedding = encode_text(question)

    # Compute similarity scores for all sentence embeddings
    similarities = [cosine_similarity(question_embedding, embedding)[0][0] for embedding in sentence_embeddings]
    
    # Find the best-matching sentence based on similarity
    best_match_idx = np.argmax(similarities)
    
    # Set a lower similarity threshold
    if similarities[best_match_idx] < 0.3:
        return "I'm not sure about that. Could you please provide more details?"

    # Return a concise answer based on the best match, with links converted
    response = convert_links(sentences[best_match_idx])

    return response.strip()

@app.route('/')
def home():
    return "Welcome to the Chatbot API!"

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')
    
    answer = get_answer(question)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)
