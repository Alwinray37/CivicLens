from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings
from ollama import ChatResponse, chat

from chunker import Chunker
from meeting_summary import MeetingSummary

# THIS IS POC, NEEDS TO BE IMPLEMENTED IN BACKEND
class ChatbotService:
    def __init__(self, db_url:str, answer_model:str):
        self.conn = None # Initialize db connection here
        self.answer_model = answer_model


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
        # we don't have embeddings stored in db at the moment, this POC will just
        # embed an example meeting
        # MeetingSummary already handles the logic for extracting text from the meeting JSON
        m_sum = MeetingSummary('ASR_Whisperx/RegularCityCouncil-9_12_25.json')
        embeddings = OllamaEmbeddings(model="qwen3-embedding:4b")
        sc = SemanticChunker(embeddings=embeddings)

        docs = sc.create_documents(texts=[m_sum.text])

        self.vstore = Chroma.from_documents(docs,embeddings)
        self.vstore = self.vstore.as_retriever(search_kwargs={"k":8})

        return self.vstore.invoke(input=question)


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
            ch_response: ChatResponse = chat(model=self.answer_model, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                    'options': {
                        'temperature': 0,
                    }
                }
            ]
            )

            return ch_response['message']['content']
