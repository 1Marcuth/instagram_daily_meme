from pydantic import validate_call
from typing import Optional, Any
import json

@validate_call
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    with open(file_path, "r", encoding = encoding) as file:
        content = file.read()

    return content

@validate_call
def write_file(file_path: str, content: str, encoding: str = "utf-8") -> None:
    with open(file_path, "w", encoding = encoding) as file:
        file.write(content)

@validate_call
def read_json_file(file_path: str, encoding: str = "utf-8") -> Any:
    data_string = read_file(file_path, encoding = encoding)
    data = json.loads(data_string)
    return data

@validate_call
def write_json_file(
    file_path: str,
    data: Any,
    indent: Optional[int] = None,
    encoding: str = "utf-8"
) -> None:
    data_string = json.dumps(data, indent = indent)
    write_file(file_path, data_string, encoding)