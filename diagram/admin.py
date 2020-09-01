from django.contrib import admin
from .models import Block, DiagFiles

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    pass

@admin.register(DiagFiles)
class FilesAdmin(admin.ModelAdmin):
    pass