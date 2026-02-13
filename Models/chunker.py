from typing import Any, Literal, Optional, TypedDict, Union
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings

type chunking_method = Literal["semantic", "fixed"]


class FixedChunkOpts(TypedDict):
    method: Literal["fixed"]
    lines_per_chunk: int
    delim: str
    overlap:int

class SemanticChunkOpts(TypedDict):
    method: Literal["semantic"]

ChunkOpts = FixedChunkOpts | SemanticChunkOpts



class Chunker:
    chunk_store: dict[str, dict[chunking_method, list[str]]] = {}

    def __init__(self, emb_model:str):
        self.emb_model = emb_model
    
    def chunk(self, text:str, key:str, opts: ChunkOpts):
        if opts["method"] == "fixed":
            return self.fixed_chunk(text=text, key=key, lines_per_chunk=opts["lines_per_chunk"], delim=opts["delim"], overlap=opts["overlap"])
        else:
            return self.semantic_chunk(text=text, key=key)



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


    def fixed_chunk(self, text:str, key:str, delim:str, lines_per_chunk:int, overlap:int=0):
        if lines_per_chunk == 0:
            return [text]

        overlap = overlap % lines_per_chunk

        keyed_chunks = self.chunk_store.get(key)

        if (keyed_chunks is not None) and ((chunks := keyed_chunks.get("semantic")) is not None):
            print(f"Retrieved {len(chunks)} semantic chunks under key {key}")
            return chunks


        i = 0
        c_id = 0
        lines = text.split(delim)

        chunks = []
        while i < len(lines):
            chunk = lines[i:i+lines_per_chunk]
            chunk_str = delim.join(chunk)
            chunks.append(chunk_str)
            i += lines_per_chunk - overlap
            c_id += 1

        if keyed_chunks is None:
            self.chunk_store[key] = {}

        self.chunk_store[key]["fixed"] = chunks

        print(f"Created {len(chunks)} fixed chunks under key {key}")
        return chunks
