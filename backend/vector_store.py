# vector_store.py

from sentence_transformers import SentenceTransformer
import faiss
import os
import sqlite3
import numpy as np

DB_PATH = "chat_logs.db"  # Corrected: should match your FastAPI app's DB path

class TicketVectorStore:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(embedding_model)
        self.index = None
        self.ticket_id_map = {}
        self._load_vectors()

    def _fetch_ticket_texts(self):
        """Fetch ticket ID, user message, and summary from the database."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_message, summary FROM chat_logs")
        data = cursor.fetchall()
        conn.close()
        return data

    def _load_vectors(self):
        """Generate and store embeddings for ticket data."""
        data = self._fetch_ticket_texts()
        if not data:
            print("No ticket data found.")
            return

        embeddings = []
        ids = []

        for row in data:
            ticket_id, user_msg, summary = row
            full_text = f"{user_msg} {summary or ''}".strip()
            vector = self.model.encode(full_text)
            embeddings.append(vector)
            ids.append(ticket_id)

        if not embeddings:
            print("No embeddings generated.")
            return

        dimension = len(embeddings[0])
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype("float32"))
        self.ticket_id_map = {i: ids[i] for i in range(len(ids))}

        print(f"✅ Indexed {len(embeddings)} tickets.")

    def search_similar_tickets(self, query: str, top_k: int = 3) -> list:
        """Search for similar tickets using the FAISS index."""
        if not self.index:
            print("❌ FAISS index is empty.")
            return []

        query_vec = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vec).astype("float32"), top_k)

        results = []
        for idx in indices[0]:
            if idx in self.ticket_id_map:
                ticket_id = self.ticket_id_map[idx]
                ticket = self._get_ticket_by_id(ticket_id)
                if ticket:
                    results.append(ticket)
        return results

    def _get_ticket_by_id(self, ticket_id: int) -> dict:
        """Retrieve a ticket's data by ID."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user_message, summary FROM chat_logs WHERE id = ?", (ticket_id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            return {
                "id": ticket_id,
                "user_message": data[0],
                "summary": data[1]
            }
        return {}
