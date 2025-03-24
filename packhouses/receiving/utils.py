from django.utils.translation import gettext_lazy as _

def get_incoming_product_categories_status():
    return [
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('quarintine', _('Quarintine')),
    ]
