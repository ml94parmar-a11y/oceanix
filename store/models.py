from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg
from django.urls import reverse

User = get_user_model()

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('failed', 'Failed'),
]

CATEGORY_CHOICES = [
    ('Kitchen', 'Kitchen'),
    ('Bathroom', 'Bathroom'),
    ('Halls', 'Halls'),
    ('Rooms', 'Rooms'),
    ('Bedrooms', 'Bedrooms'),
    ('Occasions', 'Occasions'),
    ('Others', 'Others'),
]

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default='Oceanix')
    tagline = models.CharField(max_length=500, default='Plantcare commerce for modern homes')
    whatsapp_number = models.CharField(max_length=20, default='919999999999')
    whatsapp_message = models.TextField(default='Hi Oceanix, I need help with my order.')
    footer_text = models.TextField(default='Oceanix E-Commerce Private Limited. Built with Django, AI-guided product insights, and price comparison.')

    class Meta:
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Configuration'

class SiteLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=50)
    logger_name = models.CharField(max_length=255)
    message = models.TextField()
    pathname = models.CharField(max_length=500, blank=True, null=True)
    func_name = models.CharField(max_length=200, blank=True, null=True)
    line_no = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Site Log'
        verbose_name_plural = 'Site Logs'

    def __str__(self):
        return f'[{self.timestamp}] {self.level} - {self.logger_name}'

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Others')
    image = models.CharField(max_length=255)
    ai_reference = models.TextField()
    competitor_info = models.JSONField(default=dict, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def avg_rating(self):
        result = self.reviews.aggregate(avg=Avg('rating'))
        return round(result['avg'] or 0, 1)

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.name} review by {self.user.username}'

class CartItem(models.Model):
    user = models.ForeignKey(User, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    razorpay_order_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.id} by {self.full_name}'

    def total_amount(self):
        return sum(item.total_price() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def total_price(self):
        return self.price * self.quantity
