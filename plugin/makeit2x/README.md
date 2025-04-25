## makeit2x

**Author:** caijun
**Version:** 0.0.1
**Type:** tool

### Description


```json
{
  "name": "makeit2x",
  "description": "Parse document format and can be converted to a specific format (optional).",
  "inputSchema": {
    "properties": {
      "samples": {
        "title": "samples",
        "type": "string",
        "description": "输入样本"
      },
      "outfmt": {
        "title": "out format",
        "type": "string",
        "description": "输出格式",
        "default": ""
      }
    },
    "required": ["samples"],
    "title": "makeit2xArguments",
    "type": "object"
  }
}
```