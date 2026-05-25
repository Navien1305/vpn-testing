from django import forms

from .models import City, Messenger, MobileOperator, Organization, VpnApp, VpnAppPeriod


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


class OrganizationForm(BootstrapModelForm):
    class Meta:
        model = Organization
        fields = ("name", "type", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"].required = False


class CityForm(BootstrapModelForm):
    class Meta:
        model = City
        fields = ("name", "is_active")


class MobileOperatorForm(BootstrapModelForm):
    cities = forms.ModelMultipleChoiceField(
        label="Города",
        queryset=City.objects.filter(is_active=True).order_by("name"),
        required=False,
        help_text="Можно выбрать несколько городов: Ctrl+клик или Shift+клик.",
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
    )

    class Meta:
        model = MobileOperator
        fields = ("name", "cities", "is_active")


class VpnAppForm(BootstrapModelForm):
    class Meta:
        model = VpnApp
        fields = ("name", "os", "package_id", "store_url")


class VpnAppPeriodForm(BootstrapModelForm):
    class Meta:
        model = VpnAppPeriod
        fields = ("vpn_app", "active_from", "active_to", "source_tag", "is_active", "display_order")
        widgets = {
            "active_from": forms.DateInput(attrs={"type": "date"}),
            "active_to": forms.DateInput(attrs={"type": "date"}),
        }


class MessengerForm(BootstrapModelForm):
    class Meta:
        model = Messenger
        fields = ("name", "is_active", "display_order")


class VpnAppImportForm(forms.Form):
    file = forms.FileField(
        label="Excel-файл",
        help_text="Поддерживается .xlsx с листами ТОП Android и ТОП iOS.",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx"}),
    )

    def clean_file(self):
        file = self.cleaned_data["file"]
        if not file.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("Загрузите файл в формате .xlsx.")
        return file
