from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import os
from markitdown import MarkItDown

from pydantic import BaseModel
class ToolParameters(BaseModel):
    samples: str
    outfmt: str

class Makeit2xTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        if tool_parameters.get("samples") is None:
            raise ValueError("samples is required")
        
        params = ToolParameters(**tool_parameters)
        samples = params.samples
        outfmt = params.outfmt

        # Determine if samples is a URL or a local file
        if samples.startswith("http://") or samples.startswith("https://"):
            uri = samples  # It's a URL
        elif os.path.isfile(samples):
            uri = f"file://{os.path.abspath(samples)}"  # It's a local file
        else:
            raise ValueError("samples must be a valid URL or a local file path")

        if outfmt.lower() == "markdown":
            yield self.create_text_message(MarkItDown().convert_uri(uri).markdown)
        if outfmt.lower() == "sentence":
            yield self.create_text_message(MarkItDown().convert_uri(uri).markdown)
        # yield self.create_json_message({
        #     "result": "Hello, world!"
        # })
