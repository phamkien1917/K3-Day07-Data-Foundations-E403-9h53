from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        
        # Split text into sentences using sentence-ending punctuation
        sentences = re.split(r'[.!?]+(?=\s|$)', text)
        # Remove empty sentences and strip whitespace
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
            
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed the limit, start a new chunk
            if len(current_chunk) + len(sentence) + 1 > self.max_sentences_per_chunk * 100:  # heuristic
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        
        # Try to split using the first separator, if that fails, fall back to the next
        return self._split(text, self.separators.copy())

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not remaining_separators:
            # No more separators to try, return the text as one chunk
            return [current_text]
        
        separator = remaining_separators[0]
        remaining_separators = remaining_separators[1:]
        
        # If we have a separator, split the text
        if separator and separator in current_text:
            chunks = current_text.split(separator)
            # Filter out empty chunks and strip whitespace
            chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
            
            # If any chunk is too large, recursively split it
            result = []
            for chunk in chunks:
                if len(chunk) <= self.chunk_size:
                    result.append(chunk)
                else:
                    # Recursively split this chunk
                    sub_chunks = self._split(chunk, remaining_separators)
                    result.extend(sub_chunks)
            return result
        else:
            # Try the next separator
            return self._split(current_text, remaining_separators)


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # Calculate dot product
    dot_product = _dot(vec_a, vec_b)
    
    # Calculate magnitudes
    magnitude_a = math.sqrt(_dot(vec_a, vec_a))
    magnitude_b = math.sqrt(_dot(vec_b, vec_b))
    
    # If either vector has zero magnitude, return 0
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    # Return cosine similarity
    return dot_product / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # Create instances of each chunker
        fixed_size_chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=0)
        sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)
        recursive_chunker = RecursiveChunker(chunk_size=chunk_size)
        
        # Apply each chunker to the text
        fixed_size_chunks = fixed_size_chunker.chunk(text)
        sentence_chunks = sentence_chunker.chunk(text)
        recursive_chunks = recursive_chunker.chunk(text)
        
        # Calculate statistics for each strategy
        def calculate_stats(chunks):
            if not chunks:
                return {'count': 0, 'avg_length': 0, 'chunks': []}
            return {
                'count': len(chunks),
                'avg_length': sum(len(chunk) for chunk in chunks) / len(chunks),
                'chunks': chunks
            }
        
        return {
            'fixed_size': calculate_stats(fixed_size_chunks),
            'by_sentences': calculate_stats(sentence_chunks),
            'recursive': calculate_stats(recursive_chunks)
        }
