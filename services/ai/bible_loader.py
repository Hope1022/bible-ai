# services/ai/
#   ├── bible_loader.py      ← loads and chunks Bible text into ChromaDB
#                               runs once as a setup script
#   ├── rag_service.py       ← retrieves relevant verses for any question
#   ├── chat_service.py      ← main conversation handler
#                               combines RAG + mood + history + LLM
#   ├── mood_service.py      ← reads mood history, adjusts AI tone
#   └── plan_generator.py    ← generates personalized reading plans

# routers/
#   └── ai.py               ← exposes /ai/chat, /ai/plan endpoints

# frontend/
#   └── AIChatPage.jsx       ← the chat interface
import os
import json
import glob
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import chromadb

from dotenv import load_dotenv
load_dotenv()
current_dir          = os.path.dirname(os.path.abspath(__file__))
books_dir            = os.path.join(current_dir, "books", "bible")
persistent_directory = os.path.join(current_dir, "db", "chroma_db")
COLLECTION_NAME      = "NIV_bible"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
def load_bible_documents() -> list[Document]:
    documents = []
    json_files = glob.glob(os.path.join(books_dir, "*.json"))
 
    if not json_files:
        raise FileNotFoundError(
            f"No JSON files found in {books_dir}. "
            "Make sure your Bible JSON files are in services/ai/books/bible/"
        )
 
    print(f"Found {len(json_files)} JSON files...")
 
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    data = data[0]
            except json.JSONDecodeError as e:
                print(f"Skipping {file_path} — JSON error: {e}")
                continue
 
        book_name = data.get("book", "Unknown")
        chapters  = data.get("chapters", [])
 
        for chapter_data in chapters:
            chapter_num = chapter_data.get("chapter", "?")
            verses      = chapter_data.get("verses", [])
 
            for verse_data in verses:
                verse_num = verse_data.get("verse", "?")
                text      = verse_data.get("text", "").strip()
 
                if not text:
                    continue
 
                reference = f"{book_name} {chapter_num}:{verse_num}"
 
                doc = Document(
                    page_content=f"{reference} — {text}",
                    metadata={
                        "book":        book_name,
                        "chapter":     str(chapter_num),
                        "verse":       str(verse_num),
                        "reference":   reference,
                        "translation": "NIV",
                    }
                )
                documents.append(doc)
 
    print(f"Total verses loaded: {len(documents)}")
    return documents

if not os.path.exists(persistent_directory) or not os.listdir(persistent_directory):
    print("First time running - creating vector store...")

 
    documents = load_bible_documents()
    
    print(f"Total chunks created: {len(documents)}")

    client = chromadb.PersistentClient(path=persistent_directory)

    
    db = Chroma.from_documents(
        documents,
        embeddings,
        client=client,                
        collection_name="NIV_bible"    
    )

else:
    
    client = chromadb.PersistentClient(path=persistent_directory)

    db = Chroma(
        client=client,               
        collection_name="NIV_bible",    
        embedding_function=embeddings
    )

    print(f"Total docs in DB: {db._collection.count()}")
    print("Vector store loaded!")

retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 10, "score_threshold": 0.1},
 )

question = input("\nEnter your question (or 'quit' to exit): ")
results = retriever.invoke(question)
for i, doc in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  {doc.page_content[:200]}")
            print(f"  Metadata: {doc.metadata}")
            print()
# used for finding the optimum threshold    
# test_questions = [
#     "Jesus christ",
#     "wrath of God",
#     "faith",
#     "the israelitis",
#     "psalm",
#     "the slayed lamb",
#     "dave",
#     "joy",
#     "being saved",
#     "the 10 commandements"
# ]

# for question in test_questions:
#     print(f"\nQuestion: {question}")
#     results = db.similarity_search_with_relevance_scores(question, k=3)
#     for doc, score in results:
#         print(f"Score: {score:.4f} | {doc.page_content[:60]}")
    