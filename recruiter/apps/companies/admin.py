from django.contrib import admin

from .models import (
    Company,
    CompanyInvitation,
    CompanyRequestInvitation,
)


admin.site.register(Company)
admin.site.register(CompanyInvitation)
admin.site.register(CompanyRequestInvitation)
