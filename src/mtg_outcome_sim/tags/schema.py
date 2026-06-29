from pydantic import BaseModel

class TagDefinition(BaseModel):
    name: str
    description: str
    oracle_patterns: list[str] = []
    type_line_patterns: list[str] = []
    exclude_if_tags: list[str] = []

class CardTags(BaseModel):
    card_name: str
    tags: set[str] = set()

class TagOverrides(BaseModel):
    card_name: str
    tags: set[str] = set()
