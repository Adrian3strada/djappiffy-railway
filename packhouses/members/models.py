from django.db import models
from django.utils.translation import gettext_lazy as _

class MemberWidget(models.Model):
    class Meta:
        verbose_name = _('Widgets for Member')
        verbose_name_plural = _('Widgets for Member')
