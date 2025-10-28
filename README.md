**🧠 MediChat Pro – Telegram Bot**

An intelligent AI-powered Telegram bot that allows users to upload and chat with their medical PDF documents.
MediChat Pro automatically extracts, indexes, and analyzes uploaded medical records — enabling contextual question answering using Retrieval-Augmented Generation (RAG).

**⚙️ Features**

📄 Upload and process one or more medical PDFs

🤖 Ask natural language questions about your documents

🔍 Uses FAISS vector search for relevant context retrieval

💬 Integrates Euri AI’s chat model for intelligent responses

💡 Built with LangChain, Sentence Transformers, and Telegram Bot API

**🧩 Tech Stack**

Python 3.9+

LangChain – RAG pipeline

FAISS – Vector store for semantic search

Sentence Transformers – Text embeddings

Euri AI API – LLM chat model

pdfminer.six – PDF text extraction

python-telegram-bot – Telegram bot integration

**🏗️ Environment Setup**
1. Clone the repository
git clone https://github.com/yourusername/MediChat-Pro-Telegram-Bot.git
cd MediChat-Pro-Telegram-Bot

2. Create and activate a virtual environment
🪟 On Windows:
python -m venv avivo_task_telegram_bot
avivo_task_telegram_bot\Scripts\activate

🐧 On Mac/Linux:
python3 -m venv avivo_task_telegram_bot
source avivo_task_telegram_bot/bin/activate

3. Install dependencies
pip install -r requirements.txt


**If you don’t yet have requirements.txt, create one with this content 👇**

📦 requirements.txt
python-telegram-bot==20.7
python-dotenv==1.0.1
langchain==0.2.14
langchain-community==0.2.11
faiss-cpu==1.8.0
sentence-transformers==3.0.1
pdfminer.six==20221105
EuriAI==0.1.5
PyMuPDF==1.24.1


(Versions are stable and compatible as of October 2025.)

4. Set up Environment Variables

Create a file named .env in the project root with:

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
EURI_API_KEY=your_euri_api_key_here


**💡 Get your Telegram Bot Token from @BotFather

💡 Get your Euri API key from https://euri.ai**

5. Project Structure
MediChat-Pro-Telegram-Bot/
│
├── bot.py                     # Main Telegram bot logic
├── chat_utils.py              # Handles AI chat model invocation
├── vectorstore_utils.py       # FAISS index creation & retrieval
├── requirements.txt
├── .env                       # API keys
└── data/                      # (Optional) local FAISS index folder

**🚀 Running the Bot**

Once setup is complete, simply run:

python bot.py


You should see:

🚀 MediChat Bot is running...


Then open Telegram → search for your bot → upload a PDF file → watch it automatically process → and start chatting!

**🩺 Example Flow**

Upload a medical PDF

Bot says:

“📄 Received: yourfile.pdf”

“⚙️ Processing your medical documents...”

“✅ Documents processed successfully! You can now ask your questions.”

Ask: “What are the diagnoses mentioned?”

Bot responds contextually from your uploaded reports.

**🧠 How It Works**

PDF Extraction: Uses pdfminer to extract text from medical PDFs.

Chunking: Splits long documents into overlapping text chunks using RecursiveCharacterTextSplitter.

Embedding: Converts text chunks into embeddings using SentenceTransformers.

Vector Store: Stores embeddings in a FAISS index for fast retrieval.

Question Answering: Retrieves top-matching chunks, builds a prompt, and queries the Euri AI model.
**
📚 Future Enhancements**

Add support for image-based PDFs (OCR integration).

Enable conversation memory across multiple queries.

Extend support to non-medical documents (general RAG bot).
**
🧑‍💻 Author

Nandha Kishore
**
