import os
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import (
    PDFReader,
)

class FileReaderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        input = tool_parameters.get("input")
        if input is None:
            raise ValueError("Input is required")
        
        # 检查文件是否存在
        if not os.path.exists(input):
            yield self.create_error_message(f"文件或目录不存在: {input}")
            return
        
        # PDF Reader with `SimpleDirectoryReader`
        parser = PDFReader()
        file_extractor = {".pdf": parser}
        documents = SimpleDirectoryReader(
            input_files = [input], file_extractor=file_extractor
        ).load_data()
        # 将文档列表转换为字典格式
        docs_dict = {
            "documents": [doc.dict() for doc in documents],
            "total": len(documents)
        }
        yield self.create_json_message(docs_dict)
