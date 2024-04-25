from django.contrib import admin

from  . import models

class notesAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')

admin.site.register(models.Notes, notesAdmin)
