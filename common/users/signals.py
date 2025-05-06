from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from organizations.models import OrganizationUser, OrganizationOwner
from .models import User, Group

@receiver(post_save, sender=OrganizationUser)
def add_organization_user(sender, instance, **kwargs):

    if instance.is_admin:
        user = User.objects.filter(username = instance.user_id).first()
        user.groups.add(*Group.objects.all())
    
    else:
        user = User.objects.filter(username = instance.user_id).first()
        user.groups.clear()


@receiver(post_save, sender=OrganizationOwner)
def add_organization_owner(sender, instance, **kwargs):
    user = User.objects.filter(username = instance.organization_user.user_id).first()
    user.groups.add(*Group.objects.all())
    OrganizationUser.objects.filter(id = instance.organization_user_id).update(is_admin=True,)
