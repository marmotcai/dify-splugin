from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from llama_index.readers.minio import (
    MinioReader,
)

from pydantic import BaseModel
class ToolParameters(BaseModel):
    key: str
    endpoint_url: str
    bucket: str
    minio_access_key: str
    minio_secret_key: str
    minio_secure: bool
    ollama_endpoint: str
    ollama_model_name: str

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
        ollama_embedding = None

        if len(params.ollama_endpoint) > 0:
            from llama_index.embeddings.ollama import OllamaEmbedding
            ollama_embedding = OllamaEmbedding(
                model_name = params.ollama_model_name,
                base_url = params.ollama_endpoint,
                ollama_additional_kwargs={"mirostat": 0},
            )

            pass

        result = [
            {"content": doc.text, "metadata": doc.metadata, 
             "embedding": ollama_embedding.get_query_embedding(doc.text) if ollama_embedding else ""} for doc in documents
        ]

        if params.key is None or params.key == "":
            # If no key is provided, return all documents
            yield self.create_json_message({"documents": result})
        else:
            yield self.create_json_message({params.key: result})

        
