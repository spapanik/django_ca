from typing import Literal

APIVerbs = Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE"]
JSONType = None | bool | int | float | str | list["JSONType"] | dict[str, "JSONType"]
JSONList = list[JSONType]
JSONDict = dict[str, JSONType]
