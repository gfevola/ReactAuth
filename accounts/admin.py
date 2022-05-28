from django.contrib import admin
from .models import UserAccount

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('email','name')

admin.site.register(UserAccount, UserAdmin)