from django.contrib import admin

from  . import models

class notesAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')

class categoryAdmin(admin.ModelAdmin):
    list_display = ('name')

admin.site.register(models.Notes, notesAdmin)
