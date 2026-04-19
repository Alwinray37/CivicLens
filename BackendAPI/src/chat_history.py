from typing import Any, Dict, List, Optional, override
from redisvl.extensions.constants import CONTENT_FIELD_NAME, ID_FIELD_NAME, MESSAGE_VECTOR_FIELD_NAME, METADATA_FIELD_NAME, ROLE_FIELD_NAME, TOOL_FIELD_NAME
from redisvl.extensions.message_history import ChatRole, SemanticMessageHistory
from redisvl.extensions.message_history.schema import ChatMessage
from redisvl.utils.utils import serialize, validate_vector_dims

# slight modification to redisvl SemanticMessageHistory that allows you to specify ttl
class ChatHistory(SemanticMessageHistory):
    @override
    def store(
        self, prompt: str, 
        response: str, 
        session_tag: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> None:
        self.add_messages(
            [
                {ROLE_FIELD_NAME: "user", CONTENT_FIELD_NAME: prompt},
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
