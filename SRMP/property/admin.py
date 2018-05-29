from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import *


# Define an inline admin descriptor for Notary model
# which acts a bit like a singleton
class NotaryInline(admin.StackedInline):
    model = Notary
    can_delete = False
    verbose_name_plural = 'notary'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (NotaryInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Register your models here.
admin.site.register(Notary)
admin.site.register(ReasonDocument)
admin.site.register(Object)
admin.site.register(Address)
admin.site.register(Debtor)
admin.site.register(Prosecutor)
admin.site.register(Encumbrance)
