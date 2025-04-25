from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from organizations.models import OrganizationUser
from .models import User

@receiver(post_save, sender=User)
def my_handler(sender, instance, **kwargs):
    print("llego")
    print(kwargs)

#     OrganizationUser.objects.create(
#             organization_id = creator_user.organization_id,
#             user_id = obj.username
#             )

# def save_model(self, request, obj, form, change):
#         if not obj.is_staff:
#             creator_user = OrganizationUser.objects.filter(user=request.user).first()
#             if creator_user:
#                 creator_is_owner = OrganizationOwner.objects.filter(organization = request.organization, organization_user_id=creator_user).exists()
#                 if creator_user.is_admin or creator_is_owner:
#                     obj.is_staff = True

#                     user_new = OrganizationUser.objects.filter(user_id=obj).first()
#                     if not user_new:
#                         print("llego")
#         obj.save()
