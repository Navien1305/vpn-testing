from django import forms
from django.utils import timezone

from references.models import City, MobileOperator, OperatingSystem

from .models import CheckStatus, MessengerTestForm, MessengerTestResult, TesterDevice, VpnMeasurement, VpnMeasurementResult, VpnTestForm


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
    "T2": "T2",
}


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class VpnTestFormCreateForm(BootstrapModelForm):
    device_choice = forms.ChoiceField(label="Устройство", required=False, widget=forms.Select(attrs={"class": "form-select"}))
    device_new = forms.CharField(label="Новое устройство", required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = VpnTestForm
        fields = ("city", "mobile_operator", "os")

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["city"].queryset = City.objects.filter(is_active=True).order_by("name")
        self.fields["mobile_operator"].queryset = MobileOperator.objects.filter(is_active=True).order_by("name")
        if self.user:
            user_cities = self.user.cities.filter(is_active=True).order_by("name")
            if user_cities.exists():
                self.fields["city"].queryset = user_cities
            user_mobile_operators = self.user.mobile_operators.filter(is_active=True).order_by("name")
            if user_mobile_operators.exists():
                self.fields["mobile_operator"].queryset = user_mobile_operators
        organization = getattr(self.user, "organization", None)
        if organization:
            if organization.name in UNIVERSITY_CITY_RULES:
                self.fields["city"].queryset = City.objects.filter(
                    is_active=True,
                    name=UNIVERSITY_CITY_RULES[organization.name],
                ).order_by("name")
            if organization.name in ORGANIZATION_OPERATOR_RULES:
                self.fields["mobile_operator"].queryset = MobileOperator.objects.filter(
                    is_active=True,
                    name=ORGANIZATION_OPERATOR_RULES[organization.name],
                ).order_by("name")
        devices = []
        if self.user:
            devices = list(self.user.vpn_devices.order_by("name").values_list("name", flat=True))
        if devices:
            self.fields["device_choice"].choices = [(device, device) for device in devices] + [("__new__", "Добавить новое устройство")]
            self.fields["device_new"].widget.attrs["placeholder"] = "Заполните, если выбрали новое устройство"
        else:
            self.fields["device_choice"].widget = forms.HiddenInput()
            self.fields["device_new"].required = True
            self.fields["device_new"].label = "Устройство"
        if self.user and not self.is_bound:
            user_cities = list(self.fields["city"].queryset)
            if len(user_cities) == 1:
                self.fields["city"].initial = user_cities[0]
            user_mobile_operators = list(self.fields["mobile_operator"].queryset)
            if len(user_mobile_operators) == 1:
                self.fields["mobile_operator"].initial = user_mobile_operators[0]

    def clean(self):
        cleaned_data = super().clean()
        device_choice = cleaned_data.get("device_choice")
        device_new = (cleaned_data.get("device_new") or "").strip()
        if device_choice == "__new__" and not device_new:
            self.add_error("device_new", "Укажите новое устройство.")
        elif not device_choice and not device_new:
            self.add_error("device_new", "Укажите устройство.")
        cleaned_data["device"] = device_new if device_choice in ("", "__new__", None) else device_choice
        if self.user and self.user.organization:
            exists = VpnTestForm.objects.filter(
                date=timezone.localdate(),
                organization=self.user.organization,
                city=cleaned_data.get("city"),
                mobile_operator=cleaned_data.get("mobile_operator"),
                os=cleaned_data.get("os"),
            )
            if self.instance.pk:
                exists = exists.exclude(pk=self.instance.pk)
            if all(cleaned_data.get(field) for field in ["date", "city", "mobile_operator", "os"]) and exists.exists():
                raise forms.ValidationError("VPN-анкета с такими датой, организацией, городом, оператором и ОС уже существует.")
        return cleaned_data

    def selected_device(self):
        return self.cleaned_data.get("device", "").strip()


class TestFormCreateMixin:
    device_choice = forms.ChoiceField(label="Устройство", required=False, widget=forms.Select(attrs={"class": "form-select"}))
    device_new = forms.CharField(label="Новое устройство", required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    def setup_common_fields(self):
        self.fields["city"].queryset = City.objects.filter(is_active=True).order_by("name")
        self.fields["mobile_operator"].queryset = MobileOperator.objects.filter(is_active=True).order_by("name")
        if self.user:
            user_cities = self.user.cities.filter(is_active=True).order_by("name")
            if user_cities.exists():
                self.fields["city"].queryset = user_cities
            user_mobile_operators = self.user.mobile_operators.filter(is_active=True).order_by("name")
            if user_mobile_operators.exists():
                self.fields["mobile_operator"].queryset = user_mobile_operators
        organization = getattr(self.user, "organization", None)
        if organization:
            if organization.name in UNIVERSITY_CITY_RULES:
                self.fields["city"].queryset = City.objects.filter(is_active=True, name=UNIVERSITY_CITY_RULES[organization.name]).order_by("name")
            if organization.name in ORGANIZATION_OPERATOR_RULES:
                self.fields["mobile_operator"].queryset = MobileOperator.objects.filter(is_active=True, name=ORGANIZATION_OPERATOR_RULES[organization.name]).order_by("name")
        devices = []
        if self.user:
            devices = list(self.user.vpn_devices.order_by("name").values_list("name", flat=True))
        if devices:
            self.fields["device_choice"].choices = [(device, device) for device in devices] + [("__new__", "Добавить новое устройство")]
            self.fields["device_new"].widget.attrs["placeholder"] = "Заполните, если выбрали новое устройство"
        else:
            self.fields["device_choice"].widget = forms.HiddenInput()
            self.fields["device_new"].required = True
            self.fields["device_new"].label = "Устройство"
        if self.user and not self.is_bound:
            user_cities = list(self.fields["city"].queryset)
            if len(user_cities) == 1:
                self.fields["city"].initial = user_cities[0]
            user_mobile_operators = list(self.fields["mobile_operator"].queryset)
            if len(user_mobile_operators) == 1:
                self.fields["mobile_operator"].initial = user_mobile_operators[0]

    def clean_device(self, cleaned_data):
        device_choice = cleaned_data.get("device_choice")
        device_new = (cleaned_data.get("device_new") or "").strip()
        if device_choice == "__new__" and not device_new:
            self.add_error("device_new", "Укажите новое устройство.")
        elif not device_choice and not device_new:
            self.add_error("device_new", "Укажите устройство.")
        cleaned_data["device"] = device_new if device_choice in ("", "__new__", None) else device_choice
        return cleaned_data

    def selected_device(self):
        return self.cleaned_data.get("device", "").strip()


class MessengerTestFormCreateForm(TestFormCreateMixin, BootstrapModelForm):
    device_choice = forms.ChoiceField(label="Устройство", required=False, widget=forms.Select(attrs={"class": "form-select"}))
    device_new = forms.CharField(label="Новое устройство", required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = MessengerTestForm
        fields = ("city", "mobile_operator", "os")

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.setup_common_fields()

    def clean(self):
        cleaned_data = super().clean()
        self.clean_device(cleaned_data)
        if self.user and self.user.organization:
            exists = MessengerTestForm.objects.filter(
                date=timezone.localdate(),
                organization=self.user.organization,
                city=cleaned_data.get("city"),
                mobile_operator=cleaned_data.get("mobile_operator"),
                os=cleaned_data.get("os"),
            )
            if self.instance.pk:
                exists = exists.exclude(pk=self.instance.pk)
            if all(cleaned_data.get(field) for field in ["city", "mobile_operator", "os"]) and exists.exists():
                raise forms.ValidationError("Анкета мессенджеров с такими датой, организацией, городом, оператором и ОС уже существует.")
        return cleaned_data


class VpnMeasurementResultForm(BootstrapModelForm):
    status_choices = CheckStatus.choices
    result_status_choices = (
        (CheckStatus.WORKS, CheckStatus.WORKS.label),
        (CheckStatus.NOT_WORKS, CheckStatus.NOT_WORKS.label),
    )

    class Meta:
        model = VpnMeasurementResult
        fields = ("vpn_unable_to_check", "web_with_vpn_status", "instagram_status", "youtube_status", "comment")
        widgets = {
            "vpn_unable_to_check": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in [
            "web_with_vpn_status",
            "instagram_status",
            "youtube_status",
        ]:
            self.fields[field_name].required = False
            self.fields[field_name].choices = self.result_status_choices

    def clean(self):
        cleaned_data = super().clean()
        self.instance._validated_by_result_form = True
        raw_unable_to_check = self.data.get(self.add_prefix("vpn_unable_to_check"))
        vpn_unable_to_check = cleaned_data.get("vpn_unable_to_check") or raw_unable_to_check in {"on", "true", "1", "yes"}
        if vpn_unable_to_check:
            cleaned_data["vpn_unable_to_check"] = True
            for field_name in ["web_with_vpn_status", "instagram_status", "youtube_status"]:
                self.errors.pop(field_name, None)
            if not (cleaned_data.get("comment") or "").strip():
                self.add_error("comment", "Если VPN невозможно проверить, комментарий обязателен.")
            cleaned_data["web_with_vpn_status"] = CheckStatus.NOT_APPLICABLE
            cleaned_data["instagram_status"] = CheckStatus.NOT_APPLICABLE
            cleaned_data["youtube_status"] = CheckStatus.NOT_APPLICABLE
            return cleaned_data

        if cleaned_data.get("web_with_vpn_status") == CheckStatus.WORKS:
            cleaned_data["instagram_status"] = CheckStatus.WORKS
            cleaned_data["youtube_status"] = CheckStatus.WORKS

        for field_name in ["web_with_vpn_status", "instagram_status", "youtube_status"]:
            if not cleaned_data.get(field_name):
                self.add_error(field_name, "Обязательное поле.")
        return cleaned_data


class VpnMeasurementBaselineForm(BootstrapModelForm):
    baseline_status_choices = (
        (CheckStatus.WORKS, CheckStatus.WORKS.label),
        (CheckStatus.NOT_WORKS, CheckStatus.NOT_WORKS.label),
        (CheckStatus.UNABLE_TO_CHECK, CheckStatus.UNABLE_TO_CHECK.label),
    )

    class Meta:
        model = VpnMeasurement
        fields = ("onelostbox_without_vpn_status", "onelostbox_without_vpn_comment")
        widgets = {
            "onelostbox_without_vpn_comment": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["onelostbox_without_vpn_status"].required = True
        self.fields["onelostbox_without_vpn_status"].choices = self.baseline_status_choices

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("onelostbox_without_vpn_status")
        comment = (cleaned_data.get("onelostbox_without_vpn_comment") or "").strip()
        if not status:
            raise forms.ValidationError("Заполните статус проверки onelostbox.com без VPN.")
        if status == CheckStatus.UNABLE_TO_CHECK and not comment:
            raise forms.ValidationError("При статусе 'Невозможно проверить' комментарий обязателен.")
        return cleaned_data


class ReturnMeasurementForm(forms.ModelForm):
    class Meta:
        model = VpnMeasurement
        fields = ("return_comment",)
        labels = {"return_comment": "Комментарий возврата"}
        widgets = {"return_comment": forms.Textarea(attrs={"class": "form-control", "rows": 4})}

    def clean_return_comment(self):
        value = self.cleaned_data["return_comment"].strip()
        if not value:
            raise forms.ValidationError("Укажите комментарий возврата.")
        return value


class ReturnFormForm(forms.Form):
    comment = forms.CharField(
        label="Комментарий возврата",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )


class MessengerTestResultForm(BootstrapModelForm):
    status_choices = (
        (CheckStatus.WORKS, "Работает"),
        (CheckStatus.NOT_WORKS, "Не работает"),
    )
    message_sent_at = forms.TimeField(
        label="Время отправки сообщения",
        required=False,
        input_formats=["%H:%M", "%H%M"],
        widget=forms.TimeInput(
            format="%H:%M",
            attrs={
                "class": "form-control messenger-time-input",
                "placeholder": "HH:MM",
                "inputmode": "numeric",
                "style": "width: 170px; max-width: 100%;",
            },
        ),
        error_messages={"invalid": "Введите время в формате ЧЧ:ММ."},
    )

    class Meta:
        model = MessengerTestResult
        fields = (
            "message_send_status",
            "message_sent_at",
            "file_size_mb",
            "file_send_speed_sec",
            "audio_call_status",
            "comment",
        )
        widgets = {
            "file_size_mb": forms.NumberInput(
                attrs={
                    "class": "form-control messenger-number-input",
                    "min": "0",
                    "step": "0.01",
                    "style": "width: 170px; max-width: 100%;",
                }
            ),
            "file_send_speed_sec": forms.NumberInput(
                attrs={
                    "class": "form-control messenger-number-input",
                    "min": "0",
                    "step": "0.01",
                    "style": "width: 170px; max-width: 100%;",
                }
            ),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["message_send_status", "audio_call_status"]:
            self.fields[field_name].choices = self.status_choices
            self.fields[field_name].required = False
        self.fields["message_sent_at"].required = False
        self.fields["file_size_mb"].required = False
        self.fields["file_send_speed_sec"].required = False

    def clean_file_size_mb(self):
        value = self.cleaned_data.get("file_size_mb")
        if value is not None and value < 0:
            raise forms.ValidationError("Значение не может быть меньше 0.")
        return value

    def clean_file_send_speed_sec(self):
        value = self.cleaned_data.get("file_send_speed_sec")
        if value is not None and value < 0:
            raise forms.ValidationError("Значение не может быть меньше 0.")
        return value

    def clean(self):
        cleaned_data = super().clean()
        statuses = [
            cleaned_data.get("message_send_status"),
            cleaned_data.get("audio_call_status"),
        ]
        field_names = ["message_send_status", "audio_call_status"]
        for field_name, status in zip(field_names, statuses):
            if not status:
                self.add_error(field_name, "Обязательное поле.")
        if (
            cleaned_data.get("message_send_status") == CheckStatus.WORKS
            and not cleaned_data.get("message_sent_at")
            and "message_sent_at" not in self.errors
        ):
            self.add_error("message_sent_at", "Если сообщение отправлено, укажите время отправки.")
        return cleaned_data


class ReturnMessengerForm(forms.ModelForm):
    class Meta:
        model = MessengerTestForm
        fields = ("return_comment",)
        labels = {"return_comment": "Комментарий возврата"}
        widgets = {"return_comment": forms.Textarea(attrs={"class": "form-control", "rows": 4})}

    def clean_return_comment(self):
        value = self.cleaned_data["return_comment"].strip()
        if not value:
            raise forms.ValidationError("Укажите комментарий возврата.")
        return value
