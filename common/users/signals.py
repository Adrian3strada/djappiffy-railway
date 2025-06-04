from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from organizations.models import OrganizationUser, OrganizationOwner
from .models import User, Group
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender=OrganizationUser)
def add_organization_user(sender, instance, created, raw=False, **kwargs):
    # 1) Si estamos cargando fixtures (raw=True), salimos
    # 2) Si no hay usuario relacionado, salimos
    if raw or not instance.user:
        return

    # A partir de aquí, ya existe instance.user
    if instance.is_admin:
        instance.user.groups.set(Group.objects.all())
    else:
        instance.user.groups.clear()


@receiver(post_save, sender=OrganizationOwner)
def add_organization_owner(sender, instance, **kwargs):
    user = User.objects.filter(username = instance.organization_user.user_id).first()
    user.groups.add(*Group.objects.all())
    OrganizationUser.objects.filter(id = instance.organization_user_id).update(is_admin=True,)
