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
    samples: list[File]


class FileReaderTool(Tool):
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

        # 将文档列表转换为字典格式
        docs_dict = {
            "documents": [doc.dict() for doc in documents],
            "total": len(documents)
        }
        yield self.create_json_message(docs_dict)
