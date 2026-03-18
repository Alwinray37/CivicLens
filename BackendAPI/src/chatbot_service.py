from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.vectorstores import VectorStore
from langchain_ollama import ChatOllama
from langchain_postgres import PGVectorStore, PGEngine
from langchain_core.documents import Document
from langchain_ollama.embeddings import OllamaEmbeddings

class ChatbotService:
    def __init__(self, vstore:VectorStore, chat_model:BaseChatModel):
        self.vstore = vstore
        self.chat_model = chat_model


    @classmethod
    def create(cls, db_url:str, table_name:str, embedding_model:str, answer_model:str, ollama_url:str|None=None):
        pgengine = PGEngine.from_connection_string(db_url)
        vstore = PGVectorStore.create_sync(
                engine=pgengine,
                table_name=table_name,
                embedding_service= OllamaEmbeddings(model=embedding_model, base_url=ollama_url),
                id_column="ChunkID",
                metadata_columns=["meeting_id", "ChunkNum", "StartTime", "EndTime", "Content"],
                embedding_column="Embedding",
                content_column="Content"
                )
        
        llm = ChatOllama(
                model=answer_model,
                validate_model_on_init=True,
                base_url=ollama_url,
                temperature=0,
                )
        
        return cls(vstore, llm)


    def answer(self, question:str, meeting_id:int):
        """
        Answer a question for a specific meeting
        """
        relevant_docs = self._retrieve_docs(question=question, meeting_id=meeting_id)
        prompt = self._augment(question=question, docs=relevant_docs)
        return self._generate(prompt=prompt)
    
    def _meeting_metadata_func(self, record: dict, metadata: dict) -> dict:
        metadata["start"] = record.get("start") or 0
        metadata["end"] = record.get("end") or 0
        metadata["speaker"] = record.get("speaker") or ""

        return metadata

    def _retrieve_docs(self, question:str, meeting_id:int):
        return self.vstore.similarity_search(
                query=question,
                filter={"meeting_id": { "$eq": meeting_id }},
                k=10,
                )


    def _augment(self, question:str, docs:list[Document]):
        return f"""
You are an assistant that answers questions about a city council meeting.

You are given:
- A user question
- A set of relevant excerpts from the meeting transcript

Rules:
- Answer using ONLY the information in the excerpts
- If the excerpts do not contain enough information, say "The meeting did not address this."
- Do not speculate or add outside knowledge
- Be concise and factual
- Use plain language suitable for the general public

Meeting Excerpts:
{"\n".join([d.page_content for d in docs])}

User Question:
{question}

Answer:
""".strip()


    def _generate(self, prompt:str):
            ch_response = self.chat_model.invoke(prompt)

            return ch_response.content
