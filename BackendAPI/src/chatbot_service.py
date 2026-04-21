import typing
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.vectorstores import VectorStore
from langchain_ollama import ChatOllama
from langchain_postgres import PGVectorStore, PGEngine
from langchain_core.documents import Document
from langchain_ollama.embeddings import OllamaEmbeddings
from redis import Redis
from redisvl.utils.vectorize import CustomVectorizer

from src.chat_history import ChatHistory

REDIS_URL = 'redis://redis:6379'
REDIS_TTL = 300 # seconds

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
        chat_history = ChatHistory(name='chat', distance_threshold=0.5, vectorizer=vectorizer, redis_client=redis_client, redis_url=REDIS_URL)

        return cls(vstore, llm, chat_history)


    def answer(self, question:str, meeting_id:int, session_id:str):
        """
        Answer a question for a specific meeting
        """
        if(len(question) > self.MAX_QUESTION_LEN):
            raise ChatbotException("Question is too long", status_code=414)

        meeting_session = f'{meeting_id} {session_id}'

        messages = self.chat_history.get_relevant(question, top_k=3, session_tag=meeting_session, fall_back=True)
        messages = typing.cast(list[dict[str, str]], messages)
        
        if len(messages) > 0:
            context_text = "\n".join(f'{message['role']}: {message['content']}' for message in messages)
            question = self._merge_context_and_question(context_text, question)

        print(f'QUESTION: {question}')

        relevant_docs = self._retrieve_docs(question=question, meeting_id=meeting_id)

        prompt = self._augment(question=question, docs=relevant_docs)
        response = self._generate(prompt=prompt)

        self.chat_history.store(question, str(response), ttl=REDIS_TTL)
        return response
    
    def _merge_context_and_question(self, context: str, question) -> str:
        prompt = f"""
You are a system that rewrites user questions to be fully self-contained.

You are given:
- A user question
- Relevant chat history

Your task:
Rewrite the question so that it can be understood on its own without the chat history.

Rules:
- Preserve the original meaning of the question
- Replace vague references like "it", "they", "that", or "the proposal" with specific details from the chat history
- Keep the question focused and concise
- Do NOT add new information that is not present in the chat history
- Do NOT answer the question
- Do NOT mention chat history or previous messages
- Output only the rewritten question as a single sentence

Chat History:
{context}

User Question:
{question}

Rewritten Question:
""".strip()
        response = self.chat_model.invoke(prompt).content
        assert isinstance(response, str)
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
        meeting_text = "\n".join([d.page_content for d in docs])
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
{meeting_text}

User Question:
{question}

Answer:
""".strip()


    def _generate(self, prompt:str):
            ch_response = self.chat_model.invoke(prompt)

            return ch_response.content
