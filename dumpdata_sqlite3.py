import os
import django
from django.core.management import call_command
import io

# Cấu hình settings Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop.settings")
django.setup()

# Dump dữ liệu ra file JSON với UTF-8
with io.open("data.json", "w", encoding="utf-8") as f:
    call_command(
        "dumpdata",
        "--exclude=contenttypes",
        "--exclude=auth.permission",
        "--exclude=admin",
        "--exclude=sessions",
        indent=2,
        stdout=f,
    )
