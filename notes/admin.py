from django.contrib import admin

from  . import models

class notesAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'is_public')

class categoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

class tagAdmin(admin.ModelAdmin):
    list_display = ('name',)

class profileAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_seen')

class shareGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')

class shareLinkAdmin(admin.ModelAdmin):
    list_display = ('note', 'created_by', 'created_at', 'expires_at', 'can_edit')

class shareLogAdmin(admin.ModelAdmin):
    list_display = ('note', 'action', 'actor', 'created_at')

admin.site.register(models.Notes, notesAdmin)
admin.site.register(models.Category, categoryAdmin)
admin.site.register(models.Tag, tagAdmin)
admin.site.register(models.Profile, profileAdmin)
admin.site.register(models.ShareGroup, shareGroupAdmin)
admin.site.register(models.ShareLink, shareLinkAdmin)
admin.site.register(models.NoteShareLog, shareLogAdmin)
