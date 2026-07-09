from pydantic import BaseModel


class SpellCheckResponse(BaseModel):
    word: str
    language: str
    locale: str
    is_correct: bool


class AddWordResponse(BaseModel):
    word: str
    language: str
    locale: str
    message: str


class SupportedLanguagesResponse(BaseModel):
    languages: list[str]
