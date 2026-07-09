from fastapi import FastAPI, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from dictionary_store import get_custom_words, get_dictionary, save_custom_word
from language import SUPPORTED_LANGUAGES, resolve_locale
from models import AddWordResponse, SpellCheckResponse, SupportedLanguagesResponse

app = FastAPI(
    title="Spellcheck Service",
    description="Standalone spellcheck + custom dictionary API, shared across applications.",
    version="1.0.0",
)

# Open by default since this is meant to be consumed by other internal apps.
# Lock this down to specific origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/languages", response_model=SupportedLanguagesResponse)
async def list_languages():
    return SupportedLanguagesResponse(languages=SUPPORTED_LANGUAGES)


@app.get("/spellcheck", response_model=SpellCheckResponse)
async def spellcheck_query(
    language: str = Query(...),
    word: str = Query(...),
):
    locale = resolve_locale(language)

    if not locale:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

    correct = False
    try:
        d = get_dictionary(locale)
        correct = await run_in_threadpool(d.lookup, word)
    except FileNotFoundError:
        # Base hunspell dictionary isn't available for this locale.
        # Don't hard-fail — still fall through to the custom wordlist below,
        # since a word added via /spellcheck/word should be checkable
        # even without a base dictionary present.
        pass

    # fallback: check custom wordlist
    if not correct:
        correct = word.lower() in get_custom_words(locale)

    return SpellCheckResponse(word=word, language=language, locale=locale, is_correct=correct)


@app.post("/spellcheck/word", response_model=AddWordResponse)
async def add_word_to_dictionary(
    language: str = Query(...),
    word: str = Query(...),
):
    locale = resolve_locale(language)

    if not locale:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

    w = word.lower()
    custom = get_custom_words(locale)

    if w in custom:
        raise HTTPException(
            status_code=409,
            detail=f"Word '{word}' already exists in the '{language}' dictionary.",
        )

    custom.add(w)
    await run_in_threadpool(save_custom_word, locale, w)

    return AddWordResponse(
        word=word,
        language=language,
        locale=locale,
        message=f"Word '{word}' successfully added to the '{language}' dictionary.",
    )
