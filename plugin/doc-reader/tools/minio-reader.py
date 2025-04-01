from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from llama_index.readers.minio import (
    MinioReader,
)

from pydantic import BaseModel
class ToolParameters(BaseModel):
    samples: str

class MinioReaderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        if tool_parameters.get("samples") is None:
            raise ValueError("samples is required")
        
        params = ToolParameters(**tool_parameters)
        samples = params.samples

