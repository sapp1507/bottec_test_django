from datetime import datetime

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from openpyexcel import Workbook

from orders.models import Cart, CartItem, Order, OrderItem, TGUser
from utils.converter import to_rub


@admin.register(TGUser)
class TGUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'full_name', 'username')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('tg_user', 'total_price')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'tg_user_link', 'delivery_info', 'payment_status',
                    'created_at_formatted', 'total_price', 'order_items_link')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('tg_user__username', 'tg_user__full_name', 'phone_number')
    actions = ['export_to_excel']
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('tg_user', 'is_paid')
        }),
        ('Доставка', {
            'fields': ('delivery_address', 'phone_number')
        }),
    )

    def tg_user_link(self, obj):
        url = reverse('admin:orders_tguser_change', args=[obj.tg_user.id])
        return format_html('<a href="{}">{}</a>', url, obj.tg_user)

    tg_user_link.short_description = 'Пользователь'

    def delivery_info(self, obj):
        return f"{obj.delivery_address[:30]}... | {obj.phone_number}"

    delivery_info.short_description = 'Доставка'

    def payment_status(self, obj):
        color = 'green' if obj.is_paid else 'red'
        text = 'Оплачен' if obj.is_paid else 'Не оплачен'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            text
        )

    payment_status.short_description = 'Статус оплаты'

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Дата создания'
    created_at_formatted.admin_order_field = 'created_at'

    def order_items_link(self, obj):
        count = obj.items.count()
        url = reverse('admin:orders_orderitem_changelist') + f'?order__id__exact={obj.id}'
        return format_html('<a href="{}">Товары ({})</a>', url, count)

    order_items_link.short_description = 'Товары в заказе'

    def total_price(self, obj):
        return to_rub(sum(item.price for item in obj.items.all()))

    total_price.short_description = 'Общая сумма'

    def export_to_excel(self, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.title = 'Заказы'

        # Заголовки
        headers = [
            'ID заказа',
            'Пользователь',
            'Телефон',
            'Адрес',
            'Статус оплаты',
            'Дата создания',
            'Товары',
            'Количество',
            'Цена',
            'Общая сумма'
        ]
        ws.append(headers)

        # Данные
        for order in queryset:
            for item in order.items.all():
                ws.append([
                    order.id,
                    str(order.tg_user),
                    order.phone_number,
                    order.delivery_address,
                    'Оплачен' if order.is_paid else 'Не оплачен',
                    order.created_at.strftime('%d.%m.%Y %H:%M'),
                    str(item.product),
                    item.quantity,
                    to_rub(item.product_price),
                    to_rub(item.price)
                ])

        # Форматирование
        for col in ws.columns:
            max_length = 0
            ic(col[0].column)
            column = col[0].column
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception as e:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column].width = adjusted_width

        # Сохранение
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f'orders_export_{datetime.now().strftime("%Y-%m-%d")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        wb.save(response)

        return response

    export_to_excel.short_description = 'Экспорт выбранных заказов в Excel'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_link', 'product_link', 'quantity', 'price', 'created_at')
    list_filter = ('order__is_paid', 'order__created_at', 'product')
    raw_id_fields = ('order', 'product')

    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">Заказ #{}</a>', url, obj.order.id)

    order_link.short_description = 'Заказ'
    order_link.admin_order_field = 'order'

    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product)

    product_link.short_description = 'Товар'
    product_link.admin_order_field = 'product'

    def created_at(self, obj):
        return obj.order.created_at.strftime('%d.%m.%Y %H:%M')

    created_at.short_description = 'Дата заказа'
    created_at.admin_order_field = 'order__created_at'
