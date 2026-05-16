from django.contrib import admin
from .models import CartItem, Order, OrderItem, Product, Review, SiteSettings, SiteLog

admin.site.site_header = 'Oceanix Admin Lite'
admin.site.site_title = 'Oceanix Admin'
admin.site.index_title = 'Welcome to Oceanix Admin Dashboard'

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

@admin.register(SiteLog)
class SiteLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'level', 'logger_name', 'short_message')
    list_filter = ('level', 'logger_name')
    search_fields = ('message', 'pathname', 'func_name')
    readonly_fields = ('timestamp', 'level', 'logger_name', 'message', 'pathname', 'func_name', 'line_no')
    ordering = ('-timestamp',)
    fieldsets = (
        ('Log Details', {'fields': ('timestamp', 'level', 'logger_name', 'message')}),
        ('Source', {'fields': ('pathname', 'func_name', 'line_no')}),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def short_message(self, obj):
        return obj.message[:120]
    short_message.short_description = 'Message'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'slug', 'avg_rating', 'created')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Product Info', {'fields': ('name', 'slug')}),
        ('Description & Details', {'fields': ('description', 'ai_reference')}),
        ('Pricing & Media', {'fields': ('price', 'image')}),
        ('Competitor Info', {'fields': ('competitor_info',)}),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'user__username')
    readonly_fields = ('created_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('created_at',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'amount', 'status', 'created_at')
    search_fields = ('user__username', 'full_name', 'razorpay_order_id')
    list_filter = ('status', 'created_at')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'created_at', 'updated_at')
    fieldsets = (
        ('Order Details', {'fields': ('user', 'full_name', 'email', 'phone', 'address')}),
        ('Payment Info', {'fields': ('amount', 'status', 'razorpay_order_id', 'razorpay_payment_id')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    inlines = [OrderItemInline]
