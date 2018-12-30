from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Person

@admin.register(Person)
class PersonAdmin(ImportExportModelAdmin):
    pass

# Register your models here.
