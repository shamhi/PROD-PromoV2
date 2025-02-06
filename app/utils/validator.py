from pydantic import validate_email

from app.schemas.enums import CountryEnum


def is_iso3166_country(value: str) -> bool:
    if value is None:
        return True

    try:
        CountryEnum(value.upper())
        return True
    except:  # noqa
        return False


def is_valid_email(value: str) -> bool:
    try:
        validate_email(value)
        return True
    except:  # noqa
        return False
