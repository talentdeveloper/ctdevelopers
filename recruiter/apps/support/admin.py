from django.contrib import admin

from .models import (
    Issue,
    IssueStateChange,
)

# Register your models here.
admin.site.register(Issue)
admin.site.register(IssueStateChange)
