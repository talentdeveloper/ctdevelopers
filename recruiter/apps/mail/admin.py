from django.contrib import admin

from .models import(
    EmailAlert,
    VirtualAlias,
    VirtualDomain,
    VirtualUser,
)


class MultiDBModelAdmin(admin.ModelAdmin):
    using = 'mailserver'

    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        obj.delete(using=self.using)

    def get_queryset(self, request):
        return super(MultiDBModelAdmin, self).get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super(MultiDBModelAdmin, self).formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        return super(MultiDBModelAdmin, self).formfield_for_manytomany(db_field, request, using=self.using, **kwargs)


class MultiDBTabularInline(admin.TabularInline):
    using = 'mailserver'

    def get_queryset(self, request):
        return super(MultiDBTabularInline, self).get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super(MultiDBTabularInline, self).formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        return super(MultiDBTabularInline, self).formfield_for_manytomany(db_field, request, using=self.using, **kwargs)


admin.site.register(EmailAlert, MultiDBModelAdmin)
admin.site.register(VirtualAlias, MultiDBModelAdmin)
admin.site.register(VirtualDomain, MultiDBModelAdmin)
admin.site.register(VirtualUser, MultiDBModelAdmin)
