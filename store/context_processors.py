from django.conf import settings
from .models import SiteSettings


def global_settings(request):
    cart_count = 0
    if request.user.is_authenticated:
        from .models import CartItem
        cart_count = CartItem.objects.filter(user=request.user).count()

    try:
        site_config = SiteSettings.objects.first()
        if not site_config:
            site_config = SiteSettings.objects.create()
    except:
        site_config = None

    whatsapp_number = site_config.whatsapp_number if site_config else '919999999999'
    whatsapp_message = site_config.whatsapp_message if site_config else 'Hi Oceanix, I need help with my order.'

    return {
        'LOGO_URL_PATH': settings.LOGO_URL + 'WhatsApp Image 2026-05-13 at 6.06.09 PM.jpeg',
        'WHATSAPP_CONTACT': f'https://wa.me/{whatsapp_number}?text={whatsapp_message.replace(" ", "%20")}',
        'cart_count': cart_count,
        'site_config': site_config,
    }
