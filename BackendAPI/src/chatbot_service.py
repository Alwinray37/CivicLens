import re
import typing
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.vectorstores import VectorStore
from langchain_ollama import ChatOllama
from langchain_postgres import PGVectorStore, PGEngine
from langchain_core.documents import Document
from langchain_ollama.embeddings import OllamaEmbeddings
from redis import Redis
from redisvl.query.filter import Tag
from redisvl.utils.vectorize import CustomVectorizer, EmbeddingsCache
from redisvl.extensions.cache.llm import SemanticCache

from src.chat_history import ChatHistory

REDIS_URL = 'redis://redis:6379'
REDIS_TTL = 300 # seconds

class ChatbotException(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code

class ChatbotService:
    MAX_QUESTION_LEN = 300

    def __init__(self, vstore:VectorStore, chat_model:BaseChatModel, chat_history: ChatHistory, llmcache: SemanticCache):
        self.vstore = vstore
        self.chat_model = chat_model
        self.chat_history = chat_history
        self.llmcache = llmcache


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

        
        redis_client = Redis.from_url(REDIS_URL)

        embeddings_cache = EmbeddingsCache(
                name="chatbot-embeddings-cache",
                redis_client=redis_client,
                redis_url=REDIS_URL,
                ttl=REDIS_TTL,
                )

        vectorizer = CustomVectorizer(embed=embed, embed_many=embed_many, cache=embeddings_cache)
        chat_history = ChatHistory(name='chat', distance_threshold=0.5, vectorizer=vectorizer, redis_client=redis_client, redis_url=REDIS_URL)

        llmcache = SemanticCache(
                name="chatbot-cache",
                ttl=REDIS_TTL,
                vectorizer=vectorizer,
                filterable_fields=[{"name": "meeting_id", "type": "tag"}],
                redis_client=redis_client,
                redis_url=REDIS_URL,
                distance_threshold=0.05
                )

        return cls(vstore, llm, chat_history, llmcache)


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
            context_text = "\n\n".join(f'{message['role']}: {message['content']}' for message in messages)
            print('RETRIEVED CONTEXT')
            print(context_text)
            print()
            question = self._merge_context_and_question(context_text, question)

        print('QUESTION')
        print(question)
        print()

        if responses := self.llmcache.check(question, filter_expression=Tag("meeting_id")==str(meeting_id)):
            print('CACHE HIT')
            print(responses[0]['response'])
            print()
            return responses[0]['response']

        relevant_docs = self._retrieve_docs(question=question, meeting_id=meeting_id)

        prompt = self._augment(question=question, chunks=relevant_docs)
        response = self._generate(prompt=prompt)
        
        print('RESPONSE')
        print(response)
        print()

        self.chat_history.store(question, response, ttl=REDIS_TTL)
        self.llmcache.store(question, response, filters={"meeting_id": str(meeting_id)})
        return response
    
    def _merge_context_and_question(self, context: str, question) -> str:
        prompt = f"""
You are a system that prepares user questions for retrieval.

You are given:
- A user question
- Relevant chat history

Your task:
1. Determine if the question depends on the chat history
2. Rewrite it only if necessary

Rules:
- Do NOT answer the question
- Do NOT include any explanation
- Only produce the required output format

Decision Rules:
- If the question is clear and self-contained, mark it as "standalone"
- If it depends on prior context (e.g., "it", "they", "that", "anything else"), mark it as "rewrite"

Rewriting Rules:
- Replace vague references with specific details from the chat history
- For vague follow-ups like "anything else", include the main topic from the chat history
- Do NOT add new information
- Keep it to one sentence

Output Format (must follow exactly):

TYPE: <standalone or rewrite>
QUESTION: <final question>

Chat History:
{context}

User Question:
{question}
""".strip()
        response = self.chat_model.invoke(prompt).content
        assert isinstance(response, str)

        re_match = re.match(r"TYPE:.+\sQUESTION:\s(.+)", response)
        if re_match is None:
            return response
        else:
            extracted_question = re_match.group(1)
            return extracted_question
    

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


    def _simplify_chunk_content(self, content: str):
        return re.sub(r"\|\d+\|: ", "\n", content)

    def _chunks_to_text(self, chunks: list[Document]):
        return "\n\n".join([f'[Start time: {d.metadata['StartTime']} seconds]\n{self._simplify_chunk_content(d.page_content)}'for d in chunks])

    def _augment(self, question:str, chunks:list[Document]):
        meeting_text = self._chunks_to_text(chunks)
        print('RETRIEVED CHUNKS')
        print(meeting_text)
        print()
        return f"""
You are an assistant that answers questions about a city council meeting.

You are given:
- A user question
- Relevant excerpts from the meeting transcript
- Each excerpt includes a start time in seconds

Rules:
- Answer using ONLY the information in the meeting text
- You may use timestamps to indicate when something occurred
- When including a timestamp, you MUST use this exact format:
  [TIME: <seconds>]
- Do NOT modify this format
- Do NOT convert seconds into minutes or other formats
- Only include timestamps if they are relevant to the question

Formatting Rules:
- Do NOT refer to excerpts, chunks, or transcript structure
- Do NOT mention where the information comes from
- Do NOT use markdown, bullet points, or special formatting
- Write in plain sentences only
- Be concise and factual
- Write naturally, as if explaining what happened in the meeting

Meeting Text:
{meeting_text}

User Question:
{question}

Answer:
""".strip()


    def _generate(self, prompt:str):
            ch_response = self.chat_model.invoke(prompt)
            ch_content = ch_response.content
            assert isinstance(ch_content, str)

            return ch_content
