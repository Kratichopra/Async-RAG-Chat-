  ## Async RAG Chatbot with FastAPI, Ollama, and MySQL**

This project is a fully asynchronous Retrieval-Augmented Generation (RAG) system that:

- Uses a local **LLaMA model** (via [Ollama](https://ollama.com/)) for language tasks
- Retrieves recent **presidential documents** from the Federal Register API
- Stores them in a **MySQL database**
- Summarizes them on request via a **chat-style interface built with FastAPI**

## Features

✅ Async Python backend  
✅ Ollama LLaMA model for chat  
✅ MySQL database with daily pipeline  
✅ Data-fetching tool (function calling)  
✅ Chat UI (HTML + JS + FastAPI)  
✅ Logs whether response is from model or DB

##  Tech Stack

- Python 3.11+
- FastAPI
- Jinja2 Templates
- aiomysql
- aiohttp
- Ollama (LLaMA)
- MySQL
- HTML + JS (frontend)
- dotenv for config
  
## Project Structure
Async\_RAG/
│
├── main.py                    # FastAPI app
├── agent.py                   # Chat + Tool agent logic
├── fetch\_pipeline.py          # Script to fetch and insert data from Federal Register
├── templates/
│   └── index.html             # UI for chatting
├── static/                    # (Optional) static assets like CSS/JS
├── .env                       # DB credentials
├── requirements.txt
└── README.md

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/async-rag-chat.git
cd async-rag-chat
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure you have `ollama` running with your preferred model:

```bash
ollama run llama3
```

### 3. Configure Environment

Create a `.env` file in the root directory:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=reg_data
```
### 4. Prepare MySQL Database

Create a `documents` table:

```sql
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title TEXT,
    document_number VARCHAR(255) UNIQUE,
    publication_date DATE,
    type VARCHAR(255),
    president VARCHAR(255),
    full_text_url TEXT
);
```

### 5. Run the Data Fetch Pipeline
This script pulls the past 7 days of presidential documents into MySQL:

```bash
python fetch_pipeline.py
```
### 6. Start the FastAPI App

```bash
uvicorn main:app --reload
```
Then open [http://localhost:8000](http://localhost:8000) in your browser.

##  How It Works

1. User enters a question.
2. The LLaMA model (via Ollama) decides whether it needs data from MySQL.
3. If so, a function (`get_documents_by_president`) is called.
4. The function returns 5 recent documents by the given president and month.
5. The model summarizes the data and replies in the chat.

All interactions are logged in the terminal for debugging:

* Tool usage
* Data from SQL
* Final model response

## Example Query

> "Summarize all documents by President Trump in March."

✅ The model will use the function tool, fetch from MySQL, and summarize the results.

##  Notes

* You must have [Ollama](https://ollama.com/) installed and running locally.
* CORS issues will occur if you try to open `index.html` as a local file (`file:///`). Always use the FastAPI server.
* The model used (`llama3`) can be replaced with any local Ollama model.

