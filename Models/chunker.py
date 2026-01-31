from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings


class Chunker:
    chunk_store: dict[str, dict[str, list[str]]] = {}

    def __init__(self, emb_model:str):
        self.emb_model = emb_model
    
    def semantic_chunk(self, text:str, key: str) -> list[str]:
        keyed_chunks = self.chunk_store.get(key)

        if (keyed_chunks is not None) and ((chunks := keyed_chunks.get("semantic")) is not None):

            print(f"Retrieved {len(chunks)} semantic chunks under key {key}")
            return chunks


        embeddings = OllamaEmbeddings(
                model=self.emb_model
                )

        sc = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")

        chunks = sc.split_text(text)

        if keyed_chunks is None:
            self.chunk_store[key] = {}

        self.chunk_store[key]["semantic"] = chunks

        print(f"Created {len(chunks)} semantic chunks under key {key}")

        return chunks
