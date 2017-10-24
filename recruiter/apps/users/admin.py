from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _

from .forms import (
    UserChangeForm,
    UserCreationForm,
)

from .models import (
    Agent,
    Candidate,
    CandidateSettings,
    CandidateSkill,
    CVRequest,
    Support,
    UserNote,
    UserLocation,
)


User = get_user_model()


class UserLocationFormSet(BaseInlineFormSet):
    def get_queryset(self) :
        qs = super(UserLocationFormSet, self).get_queryset()
        return qs[:5]


class UserLocationAdminInLine(admin.TabularInline):
    model = UserLocation
    formset = UserLocationFormSet
    fields = ('ip_address','city', 'country_name', 'created_at', 'see_location')
    readonly_fields = ('ip_address','city', 'country_name', 'created_at', 'see_location')
    ordering = ('-created_at',)

    def see_location(self, obj):
        return '<a href="{}" target="_blank">Visit on map</a>'.format(obj.get_on_google_maps)
    see_location.short_description = 'See on google earth'
    see_location.allow_tags = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'created_at', 'country_name', 'city', 'see_location')
    search_fields = ('user__email', 'user__first_name',)
    list_filter = ('continent_code', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 10

    def see_location(self, obj):
        return '<a href="{}" target="_blank">Visit on map</a>'.format(obj.get_on_google_maps)
    see_location.short_description = 'See on google earth'
    see_location.allow_tags = True


class UserAdmin(UserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'slug', 'account_type')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'account_type')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email', 'last_login', 'date_joined')
    inlines = [UserLocationAdminInLine,]


admin.site.register(Agent)
admin.site.register(Candidate)
admin.site.register(CandidateSettings)
admin.site.register(CandidateSkill)
admin.site.register(CVRequest)
admin.site.register(Support)
admin.site.register(User, UserAdmin)
admin.site.register(UserNote)
admin.site.register(UserLocation, UserLocationAdmin)
