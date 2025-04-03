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
        
        yield self.create_text_message(samples)
