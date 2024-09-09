from django.contrib import admin
from .models import Driver, ExitReason

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ExitReason)
class ExitReasonAdmin(admin.ModelAdmin):
    list_display = ('get_driver_name', 'reason_category', 'exit_date')
    search_fields = ('driver__name',)
    list_filter = ('reason_category', 'exit_date')

    def get_driver_name(self, obj):
        return obj.driver.name
    get_driver_name.short_description = 'Driver Name'  