from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import os
from langchain_text_splitters import MarkdownHeaderTextSplitter, CharacterTextSplitter, NLTKTextSplitter

from pydantic import BaseModel
class ToolParameters(BaseModel):
    samples: str
    infmt: str

class TextSplitterTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        if tool_parameters.get("samples") is None:
            raise ValueError("samples is required")
        
        params = ToolParameters(**tool_parameters)

        if (params.infmt.lower() == "markdown"):
            # 指定需要拆分的标题等级
            headers_to_split_on = [("#", "Header 1")]
            headers_to_split_on = [("##", "Header 2")]
            headers_to_split_on = [("###", "Header 3")]                
            # 创建MarkdownHeaderTextSplitter对象
            text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on).split_text(text = params.samples)
            result = [
                {
                "content": section.page_content,
                "metadata": section.metadata
                }
                for section in text_splitter
            ]

        elif (params.infmt.lower() == "char" or params.infmt.lower() == "nltk"):
            if (params.infmt.lower() == "char"):
                # 创建CharacterTextSplitter对象
                text_splitter = CharacterTextSplitter().split_text(text = params.samples)
            else:
                # import nltk
                # nltk.download('punkt_tab')
                text_splitter = NLTKTextSplitter(separator = "\n\n", language = "english").split_text(text = params.samples)
            result = [
                {
                "content": section,
                "metadata": {}
                }
                for section in text_splitter
            ]


        yield self.create_json_message({
            "result": result
        })
