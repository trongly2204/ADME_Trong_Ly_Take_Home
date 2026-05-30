from django.contrib import admin
from .models import AssayType, TestRequest, Compound


@admin.register(AssayType)
class AssayTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'turnaround_days', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'code']


class CompoundInline(admin.TabularInline):
    model = Compound
    extra = 0
    readonly_fields = ['drug_name', 'batch_number', 'container_barcode']


@admin.register(TestRequest)
class TestRequestAdmin(admin.ModelAdmin):
    list_display = ['pk', 'assay', 'requested_by', 'status', 'created_at']
    list_filter = ['status', 'assay__category']
    list_editable = ['status']
    inlines = [CompoundInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Compound)
class CompoundAdmin(admin.ModelAdmin):
    list_display = ['drug_name', 'batch_number', 'container_barcode', 'test_request']
    search_fields = ['drug_name', 'batch_number']
