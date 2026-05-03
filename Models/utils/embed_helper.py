import ollama

class EmbedHelper:
    embedding_models = {
        "qwen-4b" : "qwen3-embedding:4b"
    }
    
    def __init__(self, embedding_model=embedding_models["qwen-4b"]):
        self.embedding_model = embedding_model

    def embed_list(self, str_list: list[str]):
        embeddings = ollama.embed(
            model=self.embedding_model,
            input=str_list
        )
        
        return embeddings['embeddings']