from pydantic import BaseModel, ConfigDict, model_validator, field_validator

from app.core.exceptions import InvalidRequestDataError
from app.utils.validator import is_iso3166_country, is_valid_email


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def validate_fields(cls, values: "CustomBaseModel"):
        age_from = getattr(values, "age_from", None)
        age_until = getattr(values, "age_until", None)
        if age_from is not None and age_until is not None and age_from > age_until:
            raise InvalidRequestDataError

        active_from = getattr(values, "active_from", None)
        active_until = getattr(values, "active_until", None)
        if active_from is not None and active_until is not None and active_from > active_until:
            raise InvalidRequestDataError

        promo_mode = getattr(values, "mode", None)
        promo_common = getattr(values, "promo_common", None)
        promo_unique = getattr(values, "promo_unique", None)

        if promo_mode == "COMMON" and not promo_common:
            raise InvalidRequestDataError
        if promo_mode == "UNIQUE" and not promo_unique:
            raise InvalidRequestDataError
        if promo_mode == "COMMON" and promo_unique:
            raise InvalidRequestDataError
        if promo_mode == "UNIQUE" and promo_common:
            raise InvalidRequestDataError

        max_count = getattr(values, "max_count", None)
        if promo_mode == "COMMON" and max_count is not None and not (0 <= max_count <= 100000000):
            raise InvalidRequestDataError
        if promo_mode == "UNIQUE" and max_count is not None and max_count != 1:
            raise InvalidRequestDataError

        return values

    @field_validator("avatar_url", "image_url", mode="after", check_fields=False)
    def validate_url(cls, value):
        if isinstance(value, str) and "://" in value:
            if not (value.startswith("http://") or value.startswith("https://")):
                raise InvalidRequestDataError

        return value

    @field_validator("country", mode="after", check_fields=False)
    def validate_country(cls, value):
        if not is_iso3166_country(value):
            raise InvalidRequestDataError
        return value

    @field_validator("email", mode="after", check_fields=False)
    def validate_email(cls, value):
        if not is_valid_email(value):
            raise InvalidRequestDataError
        return value

    @field_validator("promo_unique", mode="after", check_fields=False)
    def validate_unique_promo_codes(cls, value):
        if value and len(value) != len(set(value)):
            raise InvalidRequestDataError
        return value

    @field_validator("categories", mode="after", check_fields=False)
    def validate_categories(cls, value):
        if value and len(value) > 20:
            raise InvalidRequestDataError
        return value
