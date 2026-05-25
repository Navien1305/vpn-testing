import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
PHONE_RE = re.compile(r"^\+?[0-9\s().-]+$")


def normalize_russian_phone(value):
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 10:
        digits = f"7{digits}"
    if len(digits) == 11 and digits[0] == "8":
        digits = f"7{digits[1:]}"
    if len(digits) == 11 and digits[0] == "7":
        return f"+7 ({digits[1:4]})-{digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    return (value or "").strip()


def validate_russian_phone(value):
    value = (value or "").strip()
    if CYRILLIC_RE.search(value) or not PHONE_RE.fullmatch(value):
        raise ValidationError("Введите корректный номер телефона РФ.")

    digits = re.sub(r"\D", "", value)
    if len(digits) != 11 or digits[0] not in ("7", "8"):
        raise ValidationError("Номер телефона РФ должен содержать 11 цифр и начинаться с +7, 7 или 8.")


def validate_contact_by_type(contact_type, value):
    if contact_type == "phone":
        validate_russian_phone(value)
        return normalize_russian_phone(value)
    if contact_type == "email":
        if CYRILLIC_RE.search(value or ""):
            raise ValidationError("Email не должен содержать кириллицу.")
        try:
            validate_email(value)
        except ValidationError as exc:
            raise ValidationError("Введите корректный email.") from exc
        return value.strip()
    raise ValidationError("Выберите тип контакта.")


def validate_contact(value):
    value = (value or "").strip()
    if not value:
        return
    if CYRILLIC_RE.search(value):
        raise ValidationError("Контакт должен быть телефоном или email без кириллицы.")

    if "@" in value:
        try:
            validate_email(value)
        except ValidationError as exc:
            raise ValidationError("Введите корректный email.") from exc
        return

    validate_russian_phone(value)
    return
