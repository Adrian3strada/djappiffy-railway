from django.dispatch import receiver
from django.db.models.signals import post_save
from organizations.models import OrganizationUser, OrganizationOwner
from .models import User, Group

# @receiver(post_save, sender=OrganizationUser)
# def add_organization_user(sender, instance, **kwargs):
#     print("add_organization_user")
#     if instance.is_admin:
#         user = User.objects.filter(username = instance.user_id).first()
#         user.groups.add(*Group.objects.all())


# @receiver(post_save, sender=OrganizationOwner)
# def add_organization_owner(sender, instance, **kwargs):
#     print("add_organization_owner")
#     user = User.objects.filter(username = instance.organization_user.id).first()
#     user.groups.add(*Group.objects.all())

#     OrganizationUser.objects.filter(id = instance.organization_user).update(is_admin=True,)
