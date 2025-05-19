# Thai RAG Terminal Chatbot

This is a simple terminal-based chatbot that uses Retrieval Augmented Generation (RAG) to answer questions in Thai based on your documents.

## Setup

1. Make sure you have Python 3.8+ installed
2. Create a virtual environment (optional but recommended):
```
python -m venv .venv
```

3. Activate the virtual environment:
   - Windows:
   ```
   .venv\Scripts\activate
   ```
   - macOS/Linux:
   ```
   source .venv/bin/activate
   ```

4. Install the required dependencies:
```
pip install -r requirements.txt
```

5. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

6. Add your text documents to the `data` folder (all `.txt` files will be processed)

## Usage

Run the chatbot with:

```
python chatbot.py
```

- Type your questions in Thai or English
- The bot will respond based on the information in your documents
- Type `exit` or `ออก` to quit the chatbot

## About

This chatbot uses:
- LangChain for RAG functionality
- OpenAI's API for embedding and LLM services
- FAISS for vector similarity search 