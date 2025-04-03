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

class FileReaderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        if tool_parameters.get("samples") is None:
            raise ValueError("samples is required")
        
        params = ToolParameters(**tool_parameters)
        samples = params.samples

        documents = SimpleDirectoryReader(
            input_files = [samples], file_extractor=None
        ).load_data()

        result = [
            {"content": doc.text, "metadata": doc.metadata} for doc in documents
        ]

        if samples is None or samples == "":
            # If no key is provided, return all documents
            yield self.create_json_message({"documents": result})
        else:
            yield self.create_json_message({samples: result})
