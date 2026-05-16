from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        from django.contrib.auth import get_user_model
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        from .models import Product, Review

        @receiver(post_migrate, dispatch_uid='store_seed_data')
        def seed_demo_data(sender, **kwargs):
            if sender.name != self.name:
                return

            User = get_user_model()
            if not User.objects.filter(username='admin').exists():
                    User.objects.create_superuser('admin', 'admin@oceanix.com', 'admin123')
            if not User.objects.filter(username='customer').exists():
                User.objects.create_user('customer', 'customer@oceanix.com', 'customer123')

            if Product.objects.exists():
                return

            items = [
                {
                    'name': 'Oceanix Indoor Green Plant',
                    'slug': 'oceanix-indoor-green-plant',
                    'description': 'A premium indoor plant for fresh air, home comfort, and easy maintenance.',
                    'price': 799.00,
                    'image': '12345.jpeg',
                    'ai_reference': 'AI suggests this plant performs well in low light and improves indoor air quality by 40%.',
                    'competitor_info': {
                        'FlipMart': '₹899',
                        'GreenKart': '₹759',
                        'EcoPlant': '₹849',
                    },
                },
                {
                    'name': 'Oceanix Outdoor Flowering Tree',
                    'slug': 'oceanix-outdoor-flowering-tree',
                    'description': 'A bright flowering tree for gardens and balconies with natural pest resistance.',
                    'price': 1499.00,
                    'image': '34634634757.jpeg',
                    'ai_reference': 'AI rating: Excellent for garden styling, compatible with moderate watering and bright sunlight.',
                    'competitor_info': {
                        'FlipMart': '₹1599',
                        'GreenKart': '₹1449',
                        'EcoPlant': '₹1525',
                    },
                },
                {
                    'name': 'Oceanix Succulent Combo Pack',
                    'slug': 'oceanix-succulent-combo-pack',
                    'description': 'A collection of easy-care succulents ideal for desktop décor and low-maintenance living.',
                    'price': 499.00,
                    'image': '5475457457.jpeg',
                    'ai_reference': 'AI suggests this set for beginners and office spaces, with drought-tolerant care guidance.',
                    'competitor_info': {
                        'FlipMart': '₹549',
                        'GreenKart': '₹479',
                        'EcoPlant': '₹520',
                    },
                },
                {
                    'name': 'Oceanix Tropical Houseplant',
                    'slug': 'oceanix-tropical-houseplant',
                    'description': 'A lush tropical houseplant suited for premium interiors and natural humidity balance.',
                    'price': 1299.00,
                    'image': '65458569.jpeg',
                    'ai_reference': 'AI recommendation: Place near a bright window and mist daily for the healthiest foliage.',
                    'competitor_info': {
                        'FlipMart': '₹1399',
                        'GreenKart': '₹1249',
                        'EcoPlant': '₹1320',
                    },
                },
            ]

            for item in items:
                Product.objects.create(**item)

            customer = User.objects.filter(username='customer').first()
            first_product = Product.objects.first()
            if customer and first_product and not Review.objects.exists():
                Review.objects.create(
                    product=first_product,
                    user=customer,
                    rating=5,
                    comment='Amazing plant and fast delivery! The AI care tips were very helpful.',
                )
