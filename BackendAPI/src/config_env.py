import os

from slowapi import Limiter
from slowapi.util import get_remote_address
from src.chatbot_service import ChatbotService
from dataclasses import dataclass

# connection strings
db_conn_str = os.getenv("DB_CONN") or ""
ollama_conn_str = os.getenv("OLLAMA_CONN") or "http://localhost:11434"
if not db_conn_str:
    db_password = os.getenv("DB_PASSWORD", "")
    db_conn_str = f"host=db dbname=postgres user=postgres password={db_password}"

split_index = db_conn_str.find(':')
db_pgv_conn_str = db_conn_str[0:split_index] + "+asyncpg" + db_conn_str[split_index:]


# models & chatbot service
answer_model = os.getenv("ANSWER_MODEL") or "smollm:135m"
embedding_model = os.getenv("EMBED_MODEL") or "all-minilm:22m"
chat_service = ChatbotService.create(db_url=db_pgv_conn_str, 
                                   answer_model=answer_model, 
                                   table_name="MeetingChunks", 
                                   embedding_model=embedding_model,
                                   ollama_url=ollama_conn_str,
                                   )

# rate limiting
chatbot_limit_strat = os.getenv("CHATBOT_LIMIT_STRAT")

match chatbot_limit_strat:
    case "IP":
        chatbot_limit_fn = get_remote_address
    case _:
        # global rate limit
        chatbot_limit_fn = lambda: "global"

chatbot_limit = os.getenv("CHATBOT_LIMIT") or "5/minute"

limiter = Limiter(key_func=chatbot_limit_fn)

@dataclass
class Env:
    db_conn: str
    chat_service: ChatbotService
    limiter: Limiter
    limit: str

env = Env(
    db_conn=db_conn_str,
    chat_service=chat_service,
    limiter=limiter,
    limit=chatbot_limit
    )
