from django.contrib import admin

# Register your models here.
from django.contrib.auth.decorators import login_required

admin.site.login = login_required(admin.site.login)
