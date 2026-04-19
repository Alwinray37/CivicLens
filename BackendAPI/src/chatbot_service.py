from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.vectorstores import VectorStore
from langchain_ollama import ChatOllama
from langchain_postgres import PGVectorStore, PGEngine
from langchain_core.documents import Document
from langchain_ollama.embeddings import OllamaEmbeddings
from redis import Redis
from redisvl.extensions.message_history import BaseMessageHistory
from redisvl.utils.vectorize import BaseVectorizer, CustomVectorizer

from src.chat_history import ChatHistory

REDIS_URL = 'redis://redis:6379'

class ChatbotException(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code

class ChatbotService:
    MAX_QUESTION_LEN = 300

    def __init__(self, vstore:VectorStore, chat_model:BaseChatModel, chat_history: ChatHistory):
        self.vstore = vstore
        self.chat_model = chat_model
        self.chat_history = chat_history


    @classmethod
    def create(cls, db_url:str, table_name:str, embedding_model:str, answer_model:str, ollama_url:str|None=None):
        pgengine = PGEngine.from_connection_string(db_url)
        embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_url)
        vstore = PGVectorStore.create_sync(
                engine=pgengine,
                table_name=table_name,
                embedding_service= embeddings,
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

        def embed(text: str):
            return embeddings.embed_query(text)
        def embed_many(texts: list[str]):
            ret = []
            for text in texts:
                ret.append(embed(text))
            return ret

        
        vectorizer = CustomVectorizer(embed=embed, embed_many=embed_many)
        redis_client = Redis.from_url(REDIS_URL)
        chat_history = ChatHistory(name='chat', distance_threshold=0.2, vectorizer=vectorizer, redis_client=redis_client, redis_url=REDIS_URL)

        return cls(vstore, llm, chat_history)


    def answer(self, question:str, meeting_id:int, session_id:str):
        """
        Answer a question for a specific meeting
        """
        if(len(question) > self.MAX_QUESTION_LEN):
            raise ChatbotException("Question is too long", status_code=414)

        meeting_session = f'{meeting_id} {session_id}'
        # cmh = RedisChatMessageHistory(session_id=f'{session_id} {meeting_id}', ttl=60, redis_url=REDIS_URL)
        messages = self.chat_history.get_relevant(question, top_k=10, session_tag=meeting_session, fall_back=True)
        print(f'HISTORY: {messages}')


        relevant_docs = self._retrieve_docs(question=question, meeting_id=meeting_id)
        prompt = self._augment(question=question, docs=relevant_docs)
        response = self._generate(prompt=prompt)

        self.chat_history.store(question, str(response))
        return response
    
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
- Relevant excerpts from the meeting transcript

Rules:
- Answer using ONLY the information in the excerpts
- Do NOT refer to excerpt numbers, chunk IDs, or any formatting of the input
- Do NOT mention "excerpt", "chunk", or "transcript" in your answer
- Write the answer as a natural response, as if explaining what happened in the meeting
- Do NOT use markdown, bullet points, or special formatting
- Use plain sentences only
- Be concise and factual
- If the excerpts do not contain enough information, say:
  "This was not discussed in the meeting."

Meeting Text:
{"\n".join([d.page_content for d in docs])}

User Question:
{question}

Answer:
""".strip()


    def _generate(self, prompt:str):
            ch_response = self.chat_model.invoke(prompt)

            return ch_response.content
