from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import PackhouseExporterSetting, PackhouseExporterProfile, OrganizationProfile
from organizations.models import Organization, OrganizationOwner
from django.db.models.signals import m2m_changed

@receiver(post_save, sender=PackhouseExporterSetting)
def add_owner(sender, instance, **kwargs):
    organization = instance.profile.organization

    if instance.user_organization:
        owner = OrganizationOwner.objects.filter(organization_user=instance.user_organization).exists()
        if not owner:
            OrganizationOwner.objects.create(
                organization_user=instance.user_organization,
                organization=organization
            )

@receiver(m2m_changed, sender=PackhouseExporterSetting.product_kinds.through)
def change_product_kinds(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        packhouse_profile = instance.profile
        packhouse_profile.product_kinds.set(instance.product_kinds.all())
        packhouse_profile.save()
    
@receiver(post_save, sender=PackhouseExporterProfile)
def change_name(sender, instance, **kwargs):
    if instance.organization:
        Organization.objects.filter(
            id=instance.organization.id
            ).update(
                name=instance.name,
            )
