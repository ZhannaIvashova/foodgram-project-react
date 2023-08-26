import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для импорта csv в базу.
    Вызов python manage.py ingredients_import из терминала в соответствующей
    папке.
    """

    help = 'Импорт csv файлов в таблицы базы.'

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        file_path = os.path.join(base_dir, 'data', 'ingredients.csv')

        with open(file_path, encoding='utf-8', mode='r') as csv_file:
            csv_read = csv.reader(csv_file)
            for row in csv_read:
                name = row[0]
                measurement_unit = row[1]

                obj, created = Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit)
                if not created:
                    self.stdout.write(
                        self.style.WARNING(f'Ингредиент {name} существует'))

        return 'Ингредиенты загружены успешно'
