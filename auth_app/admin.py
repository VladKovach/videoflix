from django.contrib import admin

from auth_app.models import User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model, displays key fields in list view."""

    list_display = ["id", "email", "is_active", "is_staff"]
