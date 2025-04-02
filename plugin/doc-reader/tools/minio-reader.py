from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from llama_index.readers.minio import (
    MinioReader,
)

from pydantic import BaseModel
class ToolParameters(BaseModel):
    endpoint_url: str
    bucket: str
    minio_access_key: str
    minio_secret_key: str
    minio_secure: bool
    key: str

mime_type_map = {
    "PDF": "application/pdf",
    "JSON": "application/json",
    "MD": "text/markdown",
    "TXT": "text/plain",
}

class MinioReaderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        params = ToolParameters(**tool_parameters)
                
        reader = MinioReader(
            minio_endpoint=params.endpoint_url,
            bucket=params.bucket,
            minio_access_key=params.minio_access_key,
            minio_secret_key=params.minio_secret_key,
            minio_secure = params.minio_secure,
            key = params.key
        )    # Read the file
        
        documents = reader.load_data()

        result = [
            {"content": doc.text, "metadata": doc.metadata} for doc in documents
        ]

        if params.key is None or params.key == "":
            # If no key is provided, return all documents
            yield self.create_json_message({"documents": result})
        else:
            yield self.create_json_message({params.key: result})

        
