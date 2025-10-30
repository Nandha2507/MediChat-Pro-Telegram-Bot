import os
import logging
import tempfile
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
)
from pdfminer.high_level import extract_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chat_utils import get_chat_model, ask_chat_model
from vectorstore_utils import create_faiss_index, retrive_relevant_docs

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- LOAD ENV ----------------
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
EURI_API_KEY = os.getenv("EURI_API_KEY")

# ---------------- SESSION STORE ----------------
user_sessions = {}  # Stores PDFs, vectorstore, chat_model, history per user


# ---------------- HELPERS ----------------
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        text = extract_text(file_path)
        return text if text.strip() else ""
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        return ""


def update_user_history(user_id, question, answer):
    """Maintain only last 3 (Q, A) pairs per user."""
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    if "history" not in user_sessions[user_id]:
        user_sessions[user_id]["history"] = []
    history = user_sessions[user_id]["history"]

    history.append({"question": question, "answer": answer})
    if len(history) > 3:
        history.pop(0)  # keep last 3 only

    user_sessions[user_id]["history"] = history


# ---------------- COMMAND HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm MediChat Bot.\n\n"
        "Please upload one or more medical PDF reports.\n"
        "Once done, type /process to process all your documents."
    )


async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Summarize last few messages or the documents."""
    user_id = update.effective_user.id
    session = user_sessions.get(user_id)

    if not session or "chat_model" not in session:
        await update.message.reply_text("⚠️ Please upload and process documents first using /process.")
        return

    chat_model = session["chat_model"]
    history = session.get("history", [])

    if history:
        conversation_text = "\n\n".join(
            [f"Q: {h['question']}\nA: {h['answer']}" for h in history]
        )
        prompt = f"""
        Summarize the recent medical chat conversation below into concise key points:

        {conversation_text}
        """
    else:
        vectorstore = session.get("vectorstore")
        if not vectorstore:
            await update.message.reply_text("⚠️ No documents found to summarize.")
            return

        prompt = "Summarize the overall key insights from the uploaded medical documents."

    try:
        summary = ask_chat_model(chat_model, prompt)
        await update.message.reply_text(f"🧾 **Summary:**\n{summary}")
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        await update.message.reply_text("⚠️ Failed to generate summary.")


async def process_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {})

    pdf_files = session.get("pdf_files", [])
    if not pdf_files:
        await update.message.reply_text("⚠️ Please upload at least one PDF first.")
        return

    await update.message.reply_text("⚙️ Processing your medical documents...")

    # Extract text from all uploaded PDFs
    all_texts = []
    for file_path in pdf_files:
        text = extract_text_from_pdf(file_path)
        if text.strip():
            # Store (filename, text) for traceability
            all_texts.append((os.path.basename(file_path), text))

    if not all_texts:
        await update.message.reply_text("⚠️ Could not extract text from the uploaded PDFs.")
        return

    # Split text into chunks tagged by filename
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
    tagged_chunks = []
    for filename, text in all_texts:
        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            tagged_chunks.append(f"[Source: {filename}]\n{chunk}")

    # Create FAISS index
    vectorstore = create_faiss_index(tagged_chunks)

    # Load chat model
    chat_model = get_chat_model(EURI_API_KEY)

    # Save session data
    user_sessions[user_id] = {
        "vectorstore": vectorstore,
        "chat_model": chat_model,
        "pdf_files": pdf_files,
        "history": []
    }

    await update.message.reply_text("✅ Documents processed successfully! You can now ask your questions.")


# ---------------- DOCUMENT HANDLER ----------------
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    document = update.message.document

    if not document.file_name.endswith(".pdf"):
        await update.message.reply_text("⚠️ Please upload a valid PDF file.")
        return

    user_dir = os.path.join(tempfile.gettempdir(), f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, document.file_name)
    file = await context.bot.get_file(document.file_id)
    await file.download_to_drive(file_path)

    session = user_sessions.get(user_id, {"pdf_files": []})
    session["pdf_files"].append(file_path)
    user_sessions[user_id] = session

    await update.message.reply_text(f"📄 Received: {document.file_name}")
    await update.message.reply_text(
        "📬 You can upload more PDFs, or type /process to process all documents."
    )


# ---------------- MESSAGE HANDLER ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text.strip()

    session = user_sessions.get(user_id)
    if not session or "vectorstore" not in session or "chat_model" not in session:
        await update.message.reply_text("⚠️ Please upload and process your documents first using /process.")
        return

    vectorstore = session["vectorstore"]
    chat_model = session["chat_model"]

    await update.message.reply_chat_action("typing")

    relevant_docs = retrive_relevant_docs(vectorstore, user_text)
    if not relevant_docs:
        await update.message.reply_text("🧠 No relevant information found in your documents.")
        return

    # Combine context + sources
    context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

    prompt = f"""
You are MediChat Pro, an intelligent assistant for medical document analysis.
Answer the question using only the context below.
If the answer is not available, say so clearly.

Context:
{context_text}

Question: {user_text}

Answer:
"""

    try:
        response = ask_chat_model(chat_model, prompt)
        await update.message.reply_text(response)
        update_user_history(user_id, user_text, response)
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        await update.message.reply_text("⚠️ Sorry, something went wrong while generating your answer.")


# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("process", process_command))
    app.add_handler(CommandHandler("summarize", summarize))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 MediChat Bot (enhanced) is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
