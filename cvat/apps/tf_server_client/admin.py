from django.contrib import admin
from .models import TFAnnotationModel

@admin.register(TFAnnotationModel)
class TFAnnotationModelAdmin(admin.ModelAdmin):
    # TODO: FIXME
    list_display = ('name', 'owner', 'created_date', 'updated_date',
        'shared', 'primary', 'framework')

    # NOTE: unsure what this code does
    def has_add_permission(self, request):
        return False
