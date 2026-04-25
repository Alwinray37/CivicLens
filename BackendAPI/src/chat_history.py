from typing import Any, Dict, List, Optional, override
from redisvl.extensions.constants import CONTENT_FIELD_NAME, ID_FIELD_NAME, MESSAGE_VECTOR_FIELD_NAME, METADATA_FIELD_NAME, ROLE_FIELD_NAME, SESSION_FIELD_NAME, TIMESTAMP_FIELD_NAME, TOOL_FIELD_NAME
from redisvl.extensions.message_history import ChatRole, SemanticMessageHistory
from redisvl.extensions.message_history.schema import ChatMessage
from redisvl.query import FilterQuery
from redisvl.query.filter import Tag
from redisvl.utils.utils import serialize, validate_vector_dims

from src.models.meeting_models import ChatResponse

# slight modification to redisvl SemanticMessageHistory that allows you to specify ttl
class ChatHistory(SemanticMessageHistory):
    @override
    def store(
        self, prompt: str, 
        response: str, 
        session_tag: Optional[str] = None,
        ttl: Optional[int] = None,
        original_prompt: Optional[str] = None,
    ) -> None:
        user_message = {ROLE_FIELD_NAME: "user", CONTENT_FIELD_NAME: prompt}

        if original_prompt is not None:
            user_message[METADATA_FIELD_NAME] = original_prompt

        self.add_messages(
            [
                user_message,
                {ROLE_FIELD_NAME: "llm", CONTENT_FIELD_NAME: response},
            ],
            session_tag,
            ttl
        )

    @override
    def add_messages(
            self, 
            messages: List[Dict[str, str]], 
            session_tag: Optional[str] = None, 
            ttl: Optional[int] = None
    ) -> None:
        session_tag = session_tag or self._session_tag
        chat_messages: List[Dict[str, Any]] = []

        for message in messages:
            content_vector = self._vectorizer.embed(message[CONTENT_FIELD_NAME])
            validate_vector_dims(
                len(content_vector),
                self._index.schema.fields[MESSAGE_VECTOR_FIELD_NAME].attrs.dims,  # type: ignore
            )

            chat_message = ChatMessage(
                role=message[ROLE_FIELD_NAME],
                content=message[CONTENT_FIELD_NAME],
                session_tag=session_tag,
                vector_field=content_vector,  # type: ignore
            )

            if TOOL_FIELD_NAME in message:
                chat_message.tool_call_id = message[TOOL_FIELD_NAME]
            if METADATA_FIELD_NAME in message:
                chat_message.metadata = serialize(message[METADATA_FIELD_NAME])

            chat_messages.append(chat_message.to_dict(dtype=self._vectorizer.dtype))

        self._index.load(data=chat_messages, id_field=ID_FIELD_NAME, ttl=ttl)

    @override
    def add_message(
        self, 
        message: Dict[str, str], 
        session_tag: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> None:
        self.add_messages([message], session_tag, ttl)

    def get_meeting_session_messages(self, meeting_id:int, session_id:str):
        meeting_session = f'{meeting_id} {session_id}'

        return_fields = [
            ID_FIELD_NAME,
            SESSION_FIELD_NAME,
            ROLE_FIELD_NAME,
            CONTENT_FIELD_NAME,
            TIMESTAMP_FIELD_NAME,
            TOOL_FIELD_NAME,
            METADATA_FIELD_NAME,
        ]

        query = FilterQuery(
            filter_expression=Tag(SESSION_FIELD_NAME) == meeting_session,
            return_fields=return_fields,
        )
        query.sort_by(TIMESTAMP_FIELD_NAME, asc=True)
        messages = self._index.query(query)

        return self._format_context(messages, as_text=False)

def cached_messages_to_responses(chat_messages: list[dict[str, str]]) -> list[ChatResponse]:
    responses = []
    for chat_message in chat_messages:
        cm_role = chat_message.get('role')
        assert cm_role is not None, "chat_message has 'role' field"

        # 'metadata' contains the original non-transformed user prompts
        # prefer these when getting message, but look for 'content' also to get
        # llm message data which is never transformed
        message_text = chat_message.get('metadata') or chat_message.get('content')
        assert message_text is not None, "chat_message has 'metadata' field"

        match cm_role:
            case ChatRole.USER:
                chat_type = "outgoing"
            case "llm":
                chat_type = "incoming"
            case _:
                assert False, "Chat messages in cache are only user or llm type"

        responses.append(ChatResponse(Response=message_text, Type=chat_type))
    return responses
