import os
from collections.abc import Generator
from typing import Any, List, cast
from pathlib import Path
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File

from llama_index.core.schema import Document
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.readers.file import (
    DocxReader,
    HWPReader,
    PDFReader,
    EpubReader,
    FlatReader,
    HTMLTagReader,
    ImageCaptionReader,
    ImageReader,
    ImageVisionLLMReader,
    IPYNBReader,
    MarkdownReader,
    MboxReader,
    PptxReader,
    PandasCSVReader,
    VideoAudioReader,
    UnstructuredReader,
    PyMuPDFReader,
    ImageTabularChartReader,
    XMLReader,
    PagedCSVReader,
    CSVReader,
    RTFReader,
)
import opendal

import yaml
import tempfile

def download_file_from_opendal(op: Any, path: str, temp_dir: str) -> str:
    """Download file from OpenDAL."""
    op = cast(opendal.AsyncOperator, op)

    print(op.stat(path).content_length)

    suffix = Path(path).suffix
    filepath = f"{temp_dir}/{next(tempfile._get_candidate_names())}{suffix}"
    with open(filepath, "wb") as f:
        f.write(op.read(path))

    return filepath

# Load configuration from a YAML file
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
config = {}
# Load configuration from file if it exists
if os.path.exists(config_path):
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)

op_s3 = opendal.Operator(
    "s3",
    root=config.get("s3", {}).get("root", "/"),
    bucket=config.get("s3", {}).get("bucket", "document"),
    endpoint=config.get("s3", {}).get("endpoint", "http://localhost:9001"),
    access_key_id=config.get("s3", {}).get("access_key_id", "admin"),
    secret_access_key=config.get("s3", {}).get("secret_access_key", "admin"),
    region=config.get("s3", {}).get("region", "us-east-1"),
)

op_fs = opendal.Operator("fs", root=config.get("fs", {}).get("root", "/root/data"))

def download_file_from_opendal(op: Any, temp_dir: str, path: str) -> str:
    """Download file from OpenDAL."""
    op = cast(opendal.AsyncOperator, op)

    print(op.stat(path).content_length)

    suffix = Path(path).suffix
    filepath = f"{temp_dir}/{next(tempfile._get_candidate_names())}{suffix}"
    with open(filepath, "wb") as f:
        f.write(op.read(path))

    return filepath

def download_dir_from_opendal(op: Any, temp_dir: str, dir: str) -> str:
    """Download directory from opendal."""
    op = cast(opendal.AsyncOperator, op)
    for obj in op.scan(dir):
        download_file_from_opendal(op, temp_dir, obj.path)

pdf_parser = PDFReader()
docx_parser = DocxReader()
file_extractor = {
    ".pdf": pdf_parser,
    ".docx": docx_parser,
    }

def load_data(op, path) -> List[Document]:
    """Load file(s) from OpenDAL."""
    with tempfile.TemporaryDirectory() as temp_dir:
        if not path.endswith("/"):
            download_file_from_opendal(op, temp_dir, path)
        else:
            download_dir_from_opendal(op, temp_dir, path)
        loader = SimpleDirectoryReader(temp_dir, file_extractor=file_extractor)
        return loader.load_data()
    
def load_data_from_http(uri) -> List[Document]:
    response = requests.get(uri)
    response.raise_for_status()  # Raise an error for bad HTTP responses
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uri).suffix) as temp_file:
        temp_file.write(response.content)
        loader = SimpleDirectoryReader(temp_file.name, file_extractor=file_extractor)
        return loader.load_data()
    return None

from llama_index.readers.file import *
from pydantic import BaseModel
import requests

class ToolParameters(BaseModel):
    samples: str

class FileReaderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        if tool_parameters.get("samples") is None:
            raise ValueError("samples is required")
        
        params = ToolParameters(**tool_parameters)
        samples = params.samples

        documents = []
        if os.path.isfile(samples):
            # If the path is a local file, load it directly
            documents = load_data(op_fs, samples)
        elif samples.startswith("http://") or samples.startswith("https://"):
            # If the path is an HTTP/HTTPS URL, download it first
            documents = load_data_from_http(samples)
        else:
            documents = load_data(op_s3, samples)

        result = [
            {"content": doc.text, "metadata": doc.metadata} for doc in documents
        ]

        if samples is None or samples == "":
            # If no key is provided, return all documents
            yield self.create_json_message({"documents": result})
        else:
            yield self.create_json_message({samples: result})
