from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Literal, Optional

type ChatRole = Literal['outgoing'] | Literal['incoming'] | Literal['error'] | Literal['pending']

class ChatResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    type: ChatRole = Field(alias="Type")
    response: str = Field(alias="Response")

class MeetingData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: datetime = Field(alias="Date")
    title: str = Field(alias="Title")
    video_url: str = Field(alias="VideoURL")
    meeting_id: int = Field(alias="MeetingID")

class MeetingsData(BaseModel):
    meetings: List[MeetingData]

class AgendaItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(alias="Title")
    meeting_id: int = Field(alias="MeetingID")
    file_number: str = Field(alias="FileNumber")
    item_number: int = Field(alias="ItemNumber")
    description: str = Field(alias="Description")
    order_number: int = Field(alias="OrderNumber")
    agenda_item_id: int = Field(alias="AgendaItemID")

class MeetingSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(alias="Title")
    summary: str = Field(alias="Summary")
    meeting_id: int = Field(alias="MeetingID")
    start_time: str = Field(alias="StartTime")
    summary_id: int = Field(alias="SummaryId")

class MeetingInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    agenda: List[AgendaItem]
    meeting: MeetingData
    documents: Optional[str] = None
    summaries: List[MeetingSummary]
    chat_history: list[ChatResponse] = Field(alias="ChatHistory")
