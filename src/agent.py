from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        # Store references to store and llm_fn
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # Retrieve top-k relevant chunks from the store
        results = self.store.search(question, top_k)
        
        # Extract the content of the chunks
        chunks = [result["content"] for result in results]
        
        # Build a prompt with the chunks as context
        context = "\n\n".join(chunks)
        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        
        # Call the LLM to generate an answer
        return self.llm_fn(prompt)
