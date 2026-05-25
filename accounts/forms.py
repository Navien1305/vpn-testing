from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Min

from references.models import City, MobileOperator, Organization, OrganizationType

from .models import User, UserRole
from .validators import validate_contact_by_type


UNIVERSITY_CITY_RULES = {
    "МТУСИ": "Москва",
    "ПГУТИ": "Самара",
    "СибГУТИ": "Новосибирск",
    "СПбГУТ": "Санкт-Петербург",
}

ORGANIZATION_OPERATOR_RULES = {
    "МТС": "МТС",
    "МегаФон": "МегаФон",
    "Мегафон": "МегаФон",
    "Билайн": "Билайн",
}


CONTACT_TYPE_CHOICES = (
    ("phone", "Телефон"),
    ("email", "Email"),
)

PUBLIC_ROLE_CHOICES = (
    (UserRole.TESTER, UserRole.TESTER.label),
    (UserRole.COORDINATOR, UserRole.COORDINATOR.label),
    (UserRole.READER, UserRole.READER.label),
)


def build_username_from_full_name(full_name):
    parts = full_name.split()
    surname, name, patronymic = parts[0], parts[1], parts[2]
    return f"{surname} {name[0].upper()}.{patronymic[0].upper()}."


def make_unique_username(base_username):
    username = base_username
    counter = 2
    while User.objects.filter(username=username).exists():
        username = f"{base_username} {counter}"
        counter += 1
    return username


class LoginForm(forms.Form):
    organization = forms.ChoiceField(label="Организация", choices=(), widget=forms.Select(attrs={"class": "form-select", "autofocus": True}))
    user_id = forms.ChoiceField(label="Логин", choices=(), widget=forms.Select(attrs={"class": "form-select"}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control"}))

    error_messages = {
        "invalid_login": "Проверьте логин и пароль.",
        "inactive": "Аккаунт отклонен или заблокирован администратором.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
        users = User.objects.select_related("organization").filter(is_active=True).order_by("organization__name", "full_name", "username")
        organization_ids = [user.organization_id for user in users if user.organization_id]
        organizations = Organization.objects.filter(id__in=organization_ids).order_by("name")
        organization_choices = [(str(org.id), org.name) for org in organizations]
        if any(user.organization_id is None for user in users):
            organization_choices.append(("__none__", "Без организации"))
        self.fields["organization"].choices = [("", "Выберите организацию")] + organization_choices
        self.fields["user_id"].choices = [("", "Выберите логин")] + [
            (str(user.id), user.username) for user in users
        ]
        self.login_users_by_organization = {}
        for user in users:
            organization_key = str(user.organization_id) if user.organization_id else "__none__"
            self.login_users_by_organization.setdefault(organization_key, []).append(str(user.id))

    def clean(self):
        cleaned_data = super().clean()
        organization = cleaned_data.get("organization")
        user_id = cleaned_data.get("user_id")
        password = cleaned_data.get("password")

        if organization and user_id and password:
            user = User.objects.filter(pk=user_id).first()
            if not user:
                raise forms.ValidationError(self.error_messages["invalid_login"], code="invalid_login")
            user_organization = str(user.organization_id) if user.organization_id else "__none__"
            if user_organization != organization:
                raise forms.ValidationError("Пользователь не относится к выбранной организации.")
            if user.check_password(password) and not user.is_active:
                raise forms.ValidationError(self.error_messages["inactive"], code="inactive")

            self.user_cache = authenticate(self.request, username=user.username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages["invalid_login"], code="invalid_login")
        return cleaned_data

    def get_user(self):
        return self.user_cache


class RegistrationForm(UserCreationForm):
    username_preview = forms.CharField(
        label="Логин",
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
        help_text="Сформируется автоматически из ФИО.",
    )
    contact_type = forms.ChoiceField(
        label="Тип контакта",
        choices=CONTACT_TYPE_CHOICES,
        initial="phone",
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
    )
    cities = forms.ModelMultipleChoiceField(
        label="Города",
        queryset=City.objects.filter(is_active=True).order_by("name"),
        required=True,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 4}),
    )
    mobile_operators = forms.ModelMultipleChoiceField(
        label="Операторы связи",
        queryset=MobileOperator.objects.filter(is_active=True).order_by("name"),
        required=True,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 4}),
    )
    role = forms.ChoiceField(
        label="Роль",
        choices=PUBLIC_ROLE_CHOICES,
        initial=UserRole.TESTER,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = User
        fields = ("full_name", "username_preview", "organization", "cities", "mobile_operators", "role", "contact_type", "contact", "password1", "password2")
        labels = {
            "full_name": "ФИО",
            "contact": "Контакт",
        }
        help_texts = {
            "full_name": "Введите полностью: фамилия, имя и отчество.",
            "contact": "Введите значение согласно выбранному типу контакта.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        organization_ids = (
            Organization.objects.filter(is_active=True)
            .exclude(type=OrganizationType.GRFC)
            .values("name", "type")
            .annotate(first_id=Min("id"))
            .values_list("first_id", flat=True)
        )
        self.fields["organization"].queryset = Organization.objects.filter(id__in=organization_ids).order_by("name")
        self.fields["organization"].required = True
        self.fields["contact"].required = False
        self.fields["contact_type"].required = False
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-control")
        self.fields["organization"].widget.attrs["class"] = "form-select"
        self.fields["contact"].widget.attrs["placeholder"] = "+7 (XXX)-XXX-XX-XX"
        self.fields["contact"].widget.attrs["class"] = "form-control contact-clear-input"
        if self.data.get("full_name"):
            try:
                self.fields["username_preview"].initial = build_username_from_full_name(" ".join(self.data.get("full_name", "").split()))
            except IndexError:
                self.fields["username_preview"].initial = ""
        city_ids_by_name = dict(City.objects.filter(is_active=True).values_list("name", "id"))
        self.organization_city_rules = {
            str(org.pk): [city_ids_by_name[UNIVERSITY_CITY_RULES[org.name]]]
            for org in self.fields["organization"].queryset
            if org.name in UNIVERSITY_CITY_RULES and UNIVERSITY_CITY_RULES[org.name] in city_ids_by_name
        }
        operator_ids_by_name = dict(MobileOperator.objects.filter(is_active=True).values_list("name", "id"))
        self.organization_operator_rules = {
            str(org.pk): [operator_ids_by_name[ORGANIZATION_OPERATOR_RULES[org.name]]]
            for org in self.fields["organization"].queryset
            if org.name in ORGANIZATION_OPERATOR_RULES and ORGANIZATION_OPERATOR_RULES[org.name] in operator_ids_by_name
        }

    def clean_full_name(self):
        full_name = " ".join((self.cleaned_data.get("full_name") or "").split())
        parts = full_name.split()
        if len(parts) < 3:
            raise forms.ValidationError("Введите полное ФИО: фамилия, имя и отчество.")
        if any(len(part.strip(".-")) < 2 for part in parts[:3]):
            raise forms.ValidationError("Фамилия, имя и отчество должны быть указаны полностью.")
        self.generated_username = make_unique_username(build_username_from_full_name(full_name))
        return full_name

    def clean(self):
        cleaned_data = super().clean()
        organization = cleaned_data.get("organization")
        full_name = cleaned_data.get("full_name")
        cities = cleaned_data.get("cities")
        mobile_operators = cleaned_data.get("mobile_operators")
        contact_type = cleaned_data.get("contact_type")
        contact = cleaned_data.get("contact")
        if organization and organization.type == OrganizationType.GRFC:
            self.add_error("organization", "ГРЧЦ недоступен для самостоятельной регистрации.")
        if full_name and organization and User.objects.filter(full_name__iexact=full_name, organization=organization).exists():
            self.add_error("full_name", "Пользователь с таким ФИО в выбранной организации уже зарегистрирован.")
        if organization and organization.name in UNIVERSITY_CITY_RULES:
            city_name = UNIVERSITY_CITY_RULES[organization.name]
            allowed_city = City.objects.filter(name=city_name, is_active=True).first()
            selected_ids = set(cities.values_list("id", flat=True)) if cities is not None else set()
            if not allowed_city or selected_ids != {allowed_city.id}:
                self.add_error("cities", f"Для {organization.name} доступен только город {city_name}.")
        if organization and organization.name in ORGANIZATION_OPERATOR_RULES:
            operator_name = ORGANIZATION_OPERATOR_RULES[organization.name]
            allowed_operator = MobileOperator.objects.filter(name=operator_name, is_active=True).first()
            selected_ids = set(mobile_operators.values_list("id", flat=True)) if mobile_operators is not None else set()
            if not allowed_operator or selected_ids != {allowed_operator.id}:
                self.add_error("mobile_operators", f"Для организации {organization.name} доступен только оператор {operator_name}.")
        if contact_type and contact:
            try:
                cleaned_data["contact"] = validate_contact_by_type(contact_type, contact)
            except ValidationError as exc:
                self.add_error("contact", exc)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = getattr(self, "generated_username", make_unique_username(build_username_from_full_name(user.full_name)))
        user.is_approved = False
        if commit:
            user.save()
            self.save_m2m()
        return user


class UserApprovalForm(forms.ModelForm):
    role = forms.ChoiceField(
        label="Роль",
        choices=PUBLIC_ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    contact_type = forms.ChoiceField(
        label="Тип контакта",
        choices=CONTACT_TYPE_CHOICES,
        initial="phone",
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
    )
    cities = forms.ModelMultipleChoiceField(
        label="Города",
        queryset=City.objects.filter(is_active=True).order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 4}),
    )
    mobile_operators = forms.ModelMultipleChoiceField(
        label="Операторы связи",
        queryset=MobileOperator.objects.filter(is_active=True).order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 4}),
    )

    class Meta:
        model = User
        fields = ("full_name", "organization", "cities", "mobile_operators", "contact_type", "contact", "role", "is_approved", "is_staff")
        labels = {
            "is_staff": "Доступ в Django Admin",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control contact-clear-input", "placeholder": "+7 (XXX)-XXX-XX-XX"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "organization": forms.Select(attrs={"class": "form-select"}),
            "is_approved": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contact"].required = False
        self.fields["contact_type"].required = False
        if self.instance and self.instance.contact:
            self.fields["contact_type"].initial = "email" if "@" in self.instance.contact else "phone"

    def clean(self):
        cleaned_data = super().clean()
        contact_type = cleaned_data.get("contact_type")
        contact = cleaned_data.get("contact")
        if contact_type and contact:
            try:
                cleaned_data["contact"] = validate_contact_by_type(contact_type, contact)
            except ValidationError as exc:
                self.add_error("contact", exc)
        return cleaned_data
