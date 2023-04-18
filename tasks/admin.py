from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ("datecreated", )  # Campos de solo lectura en el panel de administrador en tareas (atributo modelo Task)

# Register your models here.

admin.site.register(Task, TaskAdmin)