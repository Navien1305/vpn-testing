from django.core.management.base import BaseCommand

from references.models import City, MobileOperator, Organization, OrganizationType


class Command(BaseCommand):
    help = "Creates base dictionaries for the MVP."

    def handle(self, *args, **options):
        city_names = ["Москва", "Санкт-Петербург", "Самара", "Новосибирск"]
        operator_names = ["МТС", "МегаФон", "Билайн", "T2"]

        cities = {}
        for name in city_names:
            city, created = City.objects.get_or_create(name=name, defaults={"is_active": True})
            cities[name] = city
            self._write_result("Город", name, created)

        operators = {}
        for name in operator_names:
            operator, created = MobileOperator.objects.get_or_create(name=name, defaults={"is_active": True})
            operators[name] = operator
            operator.cities.set(cities.values())
            self._write_result("Оператор", name, created)

        renamed_organizations = [
            ("МГУ имени М.В. Ломоносова", "МТУСИ"),
            ("Самарский университет", "ПГУТИ"),
        ]

        for old_name, new_name in renamed_organizations:
            updated = Organization.objects.filter(name=old_name).update(
                name=new_name,
                type=OrganizationType.UNIVERSITY,
                city=None,
                is_active=True,
            )
            if updated:
                self.stdout.write(f"Организация: {old_name} переименована в {new_name}")

        university_organizations = {
            "МТУСИ": "Москва",
            "ПГУТИ": "Самара",
            "СПбГУТ": "Санкт-Петербург",
            "СибГУТИ": "Новосибирск",
        }

        organizations = [("ГРЧЦ", OrganizationType.GRFC, None, None)]
        organizations.extend(
            (name, OrganizationType.UNIVERSITY, cities[city_name], None)
            for name, city_name in university_organizations.items()
        )
        organizations.extend(
            (operator_name, OrganizationType.MOBILE_OPERATOR, cities["Москва"], operators[operator_name])
            for operator_name in ["МТС", "МегаФон", "Билайн"]
        )
        organizations.append(("T2", OrganizationType.MOBILE_OPERATOR, cities["Москва"], None))

        for name, org_type, city, linked_operator in organizations:
            organization, created = Organization.objects.get_or_create(
                name=name,
                type=org_type,
                defaults={
                    "city": city,
                    "linked_mobile_operator": linked_operator,
                    "is_active": True,
                },
            )
            if not created:
                organization.city = city
                organization.linked_mobile_operator = linked_operator
                organization.is_active = True
                organization.save(update_fields=["city", "linked_mobile_operator", "is_active", "updated_at"])
            self._write_result("Организация", name, created)

        self.stdout.write(self.style.SUCCESS("Базовые справочники подготовлены."))

    def _write_result(self, entity, name, created):
        action = "создано" if created else "уже есть"
        self.stdout.write(f"{entity}: {name} - {action}")
