from typing import Optional

LANGUAGE_LOCALE_MAP: dict[str, str] = {
    # ── Core Indian Scheduled Languages ───────────────────────────────────────
    "assamese": "as_IN",
    "bengali": "bn_IN",
    "gujarati": "gu_IN",
    "hindi": "hi_IN",
    "kannada": "kn_IN",
    "malayalam": "ml_IN",
    "manipuri": "mni_IN",  # Meitei / Manipuri
    "marathi": "mr_IN",
    "oriya": "or_IN",  # Odia
    "punjabi": "pa_IN",
    "tamil": "ta_IN",
    "telugu": "te_IN",
    "urdu": "ur_IN",

    # ── Additional Scheduled Languages ────────────────────────────────────────
    "sanskrit": "sa_IN",
    "sindhi": "sd_IN",
    "bodo": "brx_IN",
    "dogri": "doi_IN",
    "kashmiri": "ks_IN",
    "santali": "sat_IN",
    "maithili": "mai_IN",
    "konkani": "kok_IN",
    "nepali": "ne_IN",

    # ── English ───────────────────────────────────────────────────────────────
    "english": "en_US",
}


def resolve_locale(language: str) -> Optional[str]:
    """
    Accepts either a human-readable name ("Hindi") or a locale code ("hi_IN").
    Returns the locale code, or None if unrecognised.
    """
    if not language:
        return None

    # If caller already passed a locale code like "te_IN", return it directly
    if "_" in language and len(language) <= 8:
        return language.strip()

    return LANGUAGE_LOCALE_MAP.get(language.strip().lower())


SUPPORTED_LANGUAGES = list(LANGUAGE_LOCALE_MAP.keys())
