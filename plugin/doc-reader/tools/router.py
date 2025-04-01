import os
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import (
    PDFReader,
)
from pydantic import BaseModel

class ToolParameters(BaseModel):
    samples: str

mime_type_map = {
    "PDF": "application/pdf",
    "JSON": "application/json",
    "MD": "text/markdown",
    "TXT": "text/plain",
}

class RouterTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        if tool_parameters.get("samples") is None:
            raise ValueError("samples is required")
        
        params = ToolParameters(**tool_parameters)
        samples = params.samples

        # PDF Reader with `SimpleDirectoryReader`
        parser = PDFReader()  

        file_extractor = {".pdf": parser}
        documents = SimpleDirectoryReader(
            input_files = [samples], file_extractor=file_extractor
        ).load_data()

        texts = "---".join([doc.text for doc in documents])
        yield self.create_text_message(texts)

        handled_docs = [
            {"text": doc.text, "metadata": doc.metadata} for doc in documents
        ]
        yield self.create_json_message({samples: handled_docs})
        yield self.create_blob_message(
            texts.encode(),
            meta={
                "mime_type": mime_type_map["PDF"],
            },
        )