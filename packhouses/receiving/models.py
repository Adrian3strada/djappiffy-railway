from django.db import models, transaction
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import get_approval_status_choices, get_processing_status_choices, get_batch_status_change
from packhouses.catalogs.models import (WeighingScale, Supply, HarvestingCrew, Provider, ProductFoodSafetyProcess,
                                        Product, Vehicle, ProductPest, ProductDisease, ProductPhysicalDamage,
                                        ProductResidue, ProductDryMatterAcceptanceReport)
from common.base.models import Pest
from django.db.models import F, Sum
from django.core.exceptions import ValidationError


# Create your models here.
class Batch(models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_('Batch Number'), null=True, blank=True, unique=True)
    review_status = models.CharField(max_length=25, verbose_name=_('Review Status'),
                                     choices=get_approval_status_choices(), default='pending', blank=True)
    operational_status = models.CharField(max_length=25, choices=get_processing_status_choices(), default='pending',
                                          verbose_name=_('Operational Status'), blank=True)
    is_available_for_processing = models.BooleanField(default=False, verbose_name=_('Available for Processing'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'),)
    # 'parent' apunta al lote padre al que este lote fue unido.
    # Si es None, significa que el lote no ha sido unido a ningún otro.
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children', verbose_name=_('Parent'))

    def __str__(self):
        try:
            incoming = self.incomingproduct
        except IncomingProduct.DoesNotExist:
            incoming = None

        if incoming:
            sh = getattr(incoming, 'scheduleharvest', None)
            harvest_info = (
                f"{_('Schedule Harvest Number')}: {sh.ooid}"
                if sh else
                _('No Harvest')
            )
            return (
                f"{self.ooid} – {_('Incoming Product')} "
                f"id: {incoming.id} – {harvest_info}"
            )

        return f"{self.ooid} – {_('No IncomingProduct Asociated')}"

    @property
    def available_weight(self):
        if self.batchweightmovement_set.exists():
            return self.batchweightmovement_set.aggregate(
                available_weight=Sum('weight')
            )['available_weight']
        return 0

    def save(self, *args, **kwargs):
        # solo asignamos si aún no tiene ooid
        if self.ooid is None:
            with transaction.atomic():
                # bloqueamos las filas de Batch de esta organización…
                last = (
                    Batch.objects
                    .filter(organization=self.organization)
                    .order_by('-ooid')
                    .first()
                )
                self.ooid = (last.ooid + 1) if last else 1
        super().save(*args, **kwargs)

    @classmethod
    def validate_merge_batches(cls, batches_queryset):
        if batches_queryset.filter(parent__isnull=False).exists():
            raise ValidationError(
                _('You cannot merge batches that have already been merged into another batch.'),
                code='invalid_merge'
            )

        if batches_queryset.exclude(review_status='accepted').exists():
            raise ValidationError(
                _('Only batches with a Review Status of “Accepted” can be merged.'),
                code='invalid_status'
            )

        prefix = 'incomingproduct__scheduleharvest__'
        checks = {
            _('provider'): prefix + 'product_provider',
            _('product'): prefix + 'product',
            _('variety'): prefix + 'product_variety',
            _('phenology'): prefix + 'product_phenologies',
        }

        for label, path in checks.items():
            if batches_queryset.values_list(path, flat=True).distinct().count() != 1:
                msg = _('All batches selected must have the same %(label)s.') % {'label': label}
                raise ValidationError(msg, code='invalid_merge')
    
    @classmethod
    def validate_add_batches_to_existing_merge(cls, parent, candidate_batches):
        if parent.parent is not None:
            raise ValidationError(
                _('The selected destination batch is already merged into another batch.'),
                code='invalid_target'
            )

        if candidate_batches.exclude(review_status='accepted').exists():
            raise ValidationError(
                _('Only batches with a Review Status of “Accepted” can be merged.'),
                code='invalid_status'
            )

        child_ids = list(parent.children.values_list('pk', flat=True))
        candidate_ids = list(candidate_batches.values_list('pk', flat=True))
        combined_ids = child_ids + candidate_ids

        all_batches = Batch.objects.filter(pk__in=combined_ids)

        prefix = 'incomingproduct__scheduleharvest__'
        checks = {
            _('provider'): prefix + 'product_provider',
            _('product'):  prefix + 'product',
            _('variety'):  prefix + 'product_variety',
            _('phenology'): prefix + 'product_phenologies',
        }

        for label, path in checks.items():
            if all_batches.values_list(path, flat=True).distinct().count() != 1:
                raise ValidationError(
                    _('All batches to be merged must have the same %(label)s as the already merged ones.') % {'label': label},
                    code='invalid_merge'
                )
    
    @property
    def is_child(self):
        return self.parent is not None

    @property
    def is_parent(self):
        return self.children.exists()

    @property
    def children_list(self):
        return self.children.all()

    @property
    def children_ooids(self):
        return ", ".join(str(batch.ooid) for batch in self.children.all())

    @property
    def parent_ooid(self):
        return self.parent.ooid if self.parent else ''
    
    @property
    def children_total_weight_received(self):
        total = 0
        for child in self.children.all():
            ip = getattr(child, 'incomingproduct', None)
            if not ip:
                continue
            if ip.packhouse_weight_result:
                total += ip.packhouse_weight_result
        return total

    def operational_status_history(self):
        return self.batchstatuschange_set.filter(field_name='operational_status')

    def review_status_history(self):
        return self.batchstatuschange_set.filter(field_name='review_status')

    def last_operational_status_change(self):
        return self.operational_status_history().order_by('-created_at').first()

    def last_review_status_change(self):
        return self.review_status_history().order_by('-created_at').first()

    class Meta:
        verbose_name = _('Batch')
        verbose_name_plural = _('Batches')
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'ooid'],
                name='unique_batch_ooid_per_org'
            )
        ]


class BatchWeightMovement(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, verbose_name=_('Batch'))
    weight = models.FloatField(default=0, verbose_name=_('Weight'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    def __str__(self):
        return f"{self.batch} {self.created_at} :: {self.weight}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Batch Weight Movement')
        verbose_name_plural = _('Batch Weight Movements')

    def clean(self):
        if self.weight < 0 and self.batch.available_weight + self.weight < 0:
            raise ValidationError(
                _('This movement would result in a negative weight for the batch.'),
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class BatchStatusChange(models.Model):
    field_name = models.CharField(max_length=32, choices=get_batch_status_change, )
    created_at = models.DateTimeField(auto_now_add=True)
    old_status = models.CharField(max_length=25)
    new_status = models.CharField(max_length=25)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, verbose_name=_('Batch'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'), )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['batch', 'field_name', 'created_at']),
        ]
        verbose_name = _('Batch Status Change')
        verbose_name_plural = _('Batch Status Changes')

    def __str__(self):
        return (
            f"{self.new_status!r} {_('at')} {self.created_at} — "
            f"{self.get_field_name_display()} for {_('Batch')} {self.batch.pk} "
            f"(was {self.old_status!r})"
        )


class IncomingProduct(models.Model):
    status = models.CharField(max_length=20, verbose_name=_('Status'), choices=get_approval_status_choices(),
                              default='pending')
    public_weighing_scale = models.ForeignKey(WeighingScale, verbose_name=_("Public Weighing Scale"),
                                              on_delete=models.PROTECT, null=True, blank=False)
    public_weight_result = models.FloatField(default=0, verbose_name=_("Public Weight Result"), )
    packhouse_weight_result = models.FloatField(default=0, verbose_name=_("Packhouse Weight Result"), )
    weighing_record_number = models.CharField(max_length=30, verbose_name=_('Weighing Record Number'), )
    total_weighed_sets = models.PositiveIntegerField(default=0, verbose_name=_('Total Weighed Sets'))
    mrl = models.FloatField(default=0, verbose_name=_('Maximum Residue Limit'), null=True, blank=True)
    phytosanitary_certificate = models.CharField(max_length=50, verbose_name=_('Phytosanitary Certificate'), null=True,
                                                 blank=True)
    kg_sample = models.FloatField(default=0, verbose_name=_("Kg for Sample"), validators=[MinValueValidator(0.01)])
    containers_assigned = models.PositiveIntegerField(default=0, verbose_name=_('Containments Assigned'),
                                                      help_text=_('Containments assigned per harvest'))
    empty_containers = models.PositiveIntegerField(default=0, verbose_name=_('Empty Containments'),
                                                   help_text=_('Empty containments per harvest'))
    total_weighed_set_containers = models.PositiveIntegerField(default=0,
                                                               verbose_name=_('Total Weighed Set Containments'))
    full_containers_per_harvest = models.PositiveIntegerField(default=0,
                                                              verbose_name=_('Full Containments per Harvest'), )
    missing_containers = models.IntegerField(default=0, verbose_name=_('Missing Containments'),
                                             help_text=_('Missing containments per harvest'))
    average_per_container = models.FloatField(default=0, verbose_name=_("Average per Container"), help_text=_(
        'Based on packhouse weight result and weighed set containments'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'))
    batch = models.OneToOneField(Batch, on_delete=models.PROTECT, verbose_name=_('Batch'), null=True, blank=True)
    comments = models.TextField(verbose_name=_("Comments"), blank=True, null=True)

    @property
    def packhouse_result_weight(self):
        if self.public_weight_result:
            return self.public_weight_result
        return 0

    def clean(self):
        if self.pk:
            initial_status = IncomingProduct.objects.get(pk=self.pk).status
            if initial_status == 'accepted' and self.status != 'accepted':
                raise ValidationError("Once accepted, the status cannot be changed.")

        if self.status == "accepted" and not self.weighingset_set.exists():
            raise ValidationError("At least one Weighing Set must be registered for the Incoming Product.")

    def save(self, *args, **kwargs):
        self.clean()

        previous_status = 'pending'
        if self.pk:
            previous_status = IncomingProduct.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        if self.status == 'accepted' and previous_status != 'accepted' and self.batch_id is None:
            with transaction.atomic():
                new_batch = Batch.objects.create(
                    review_status='pending',
                    operational_status='pending',
                    is_available_for_processing=False,
                    organization=self.organization
                )
                self.batch = new_batch
                BatchWeightMovement.objects.create(
                    batch=new_batch,
                    weight=self.packhouse_weight_result
                )
                super().save(update_fields=['batch'])

    def __str__(self):
        # from packhouses.gathering.models import ScheduleHarvest
        # schedule_harvest = ScheduleHarvest.objects.filter(incoming_product=self).first()
        # TODO: Jaqueline: Validar que este cambio funciona bien, si si, eliminar estos tres comentarios
        schedule_harvest = self.scheduleharvest
        if schedule_harvest:
            return f"{schedule_harvest.ooid} - {schedule_harvest.orchard}"
        return self.id

    class Meta:
        verbose_name = _('Incoming Product')
        verbose_name_plural = _('Incoming Product')
        """constraints = [
            models.UniqueConstraint(
                fields=['harvest', 'organization'],
                name='unique_incoming_product_harvest'
            )
        ]"""


class WeighingSet(models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_("ID"), null=True, blank=True)
    provider = models.ForeignKey(Provider, verbose_name=_('Harvesting Crew Provider'), on_delete=models.CASCADE, )
    harvesting_crew = models.ForeignKey(HarvestingCrew, verbose_name=_("Harvesting Crew"), on_delete=models.CASCADE, )
    gross_weight = models.FloatField(default=0.0, verbose_name=_("Gross Weight"), )
    total_containers = models.PositiveIntegerField(default=0, verbose_name=_('Total Containments'))
    container_tare = models.FloatField(default=0.0, verbose_name=_("Container Tare"), )
    platform_tare = models.FloatField(default=0.0, verbose_name=_("Platform Tare"), )
    net_weight = models.FloatField(default=0.0, verbose_name=_("Net Weight"), )
    incoming_product = models.ForeignKey(IncomingProduct, verbose_name=_('Incoming Product'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.ooid}"

    def save(self, *args, **kwargs):
        if not self.ooid:
            with transaction.atomic():
                last_ws = (
                    WeighingSet.objects
                    .select_for_update()
                    .filter(incoming_product=self.incoming_product)
                    .order_by('-ooid')
                    .first()
                )
                self.ooid = (last_ws.ooid + 1) if last_ws else 1

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Captura el incoming_product y el ooid antes de borrar
        inc = self.incoming_product
        deleted_ooid = self.ooid
        with transaction.atomic():
            super().delete(*args, **kwargs)
            # Decrementa en 1 todos los ooid > eliminado para reacomodar
            WeighingSet.objects.filter(
                incoming_product=inc,
                ooid__gt=deleted_ooid
            ).update(ooid=F('ooid') - 1)

    class Meta:
        verbose_name = _('Weighing Set')
        verbose_name_plural = _('Weighing Sets')
        constraints = [
            models.UniqueConstraint(fields=['incoming_product', 'ooid'], name='weighing_unique_incomingproduct')
        ]


class WeighingSetContainer(models.Model):
    harvest_container = models.ForeignKey(Supply, on_delete=models.CASCADE,
                                          limit_choices_to={'kind__category': 'harvest_container'},
                                          verbose_name=_('Harvest Containments'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    weighing_set = models.ForeignKey(WeighingSet, verbose_name=_('Incoming Product'), on_delete=models.CASCADE,
                                     null=True, blank=True)

    class Meta:
        verbose_name = _('Weighing Set Containment')
        verbose_name_plural = _('Weighing Sets Containments')


class FoodSafety(models.Model):
    batch = models.OneToOneField(Batch, verbose_name=_('Batch'), on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'), )

    def __str__(self):
        return f"{self.batch}"

    class Meta:
        verbose_name = _('Food Safety')
        verbose_name_plural = _('Food Safeties')


class DryMatter(models.Model):
    product_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paper_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    moisture_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dry_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dry_matter = models.DecimalField(max_digits=10, decimal_places=2)
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Dry Matter')
        verbose_name_plural = _('Dry Matters')


class InternalInspection(models.Model):
    internal_temperature = models.DecimalField(max_digits=10, decimal_places=2)
    product_pest = models.ManyToManyField(ProductPest, verbose_name=_('Pests'), blank=True)
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Internal Inspection')
        verbose_name_plural = _('Internal Inspections')


class Average(models.Model):
    average_dry_matter = models.DecimalField(default=0, max_digits=10, decimal_places=2,
                                             verbose_name=_('Average Dry Matter'))
    average_internal_temperature = models.DecimalField(default=0, max_digits=10, decimal_places=2,
                                                       verbose_name=_('Average Internal Temperature'))
    acceptance_report = models.ForeignKey(ProductDryMatterAcceptanceReport, verbose_name=_('Acceptance Report'),
                                          on_delete=models.CASCADE, null=True)
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Average')
        verbose_name_plural = _('Averages')


class VehicleReview(models.Model):
    vehicle = models.ForeignKey('gathering.ScheduleHarvestVehicle', verbose_name=_('Vehicle'), on_delete=models.CASCADE)
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.vehicle} / {self.vehicle.stamp_number}"

    class Meta:
        verbose_name = _('Vehicle Review')
        verbose_name_plural = _('Vehicle Reviews')
        constraints = [
            models.UniqueConstraint(
                fields=['food_safety', 'vehicle'],
                name='unique_food_safety_vehicle'),
        ]


class VehicleInspection(models.Model):
    sealed = models.BooleanField(default=False, verbose_name=_('The vehicle is sealed'))
    only_the_product = models.BooleanField(default=False, verbose_name=_('The vehicle carries only the product'))
    free_foreign_matter = models.BooleanField(default=False, verbose_name=_('The vehicle is free of foreign matter'))
    free_unusual_odors = models.BooleanField(default=False, verbose_name=_('The vehicle is free of unusual odors'))
    certificate = models.BooleanField(default=False, verbose_name=_('Has a CERTIFICATE'))
    free_fecal_matter = models.BooleanField(default=False, verbose_name=_('The vehicle is free of fecal matter'))
    vehicle_review = models.ForeignKey(VehicleReview, verbose_name=_('Vehicle Review'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Vehicle Inspection')
        verbose_name_plural = _('Vehicle Inspections')


class VehicleCondition(models.Model):
    is_clean = models.BooleanField(default=False, verbose_name=_('It is clean'))
    good_condition = models.BooleanField(default=False, verbose_name=_('Good condition'))
    broken = models.BooleanField(default=False, verbose_name=_('Broken'))
    damaged = models.BooleanField(default=False, verbose_name=_('Damaged'))
    seal = models.BooleanField(default=False, verbose_name=_('Seal'))
    vehicle_review = models.ForeignKey(VehicleReview, verbose_name=_('Vehicle Review'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Vehicle Condition')
        verbose_name_plural = _('Vehicle Conditions')

    def __str__(self):
        return f""


class SampleCollection(models.Model):
    whole = models.BooleanField(default=False, verbose_name=_('Whole'))
    foreign_material = models.BooleanField(default=False, verbose_name=_('Foreign Material'))
    insects = models.BooleanField(default=False, verbose_name=_('Insects'))
    temperature_damage = models.BooleanField(default=False, verbose_name=_('Temperature Damage'))
    unusual_odor = models.BooleanField(default=False, verbose_name=_('Unusual Odor'))
    food_safety = models.ForeignKey(FoodSafety, verbose_name=_('Food Safety'), on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Sample Collection')
        verbose_name_plural = _('Sample Collections')


class SampleWeight(models.Model):
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'),
                                          on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Sample Weight')
        verbose_name_plural = _('Sample Weights')


class SamplePest(models.Model):
    sample_pest = models.IntegerField(verbose_name=_('Samples With Pests'))
    product_pest = models.ForeignKey(ProductPest, verbose_name=_('Pest'), on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Percentage'), null=True,
                                     blank=True)
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'),
                                          on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Sample Pest')
        verbose_name_plural = _('Sample Pests')
        constraints = [
            models.UniqueConstraint(
                fields=['sample_collection', 'product_pest'],
                name='unique_sample_collection_product_pest'),
        ]

    def save(self, *args, **kwargs):
        total_sample_weight = SampleWeight.objects.filter(sample_collection=self.sample_collection).count()
        self.percentage = (self.sample_pest / total_sample_weight) * 100

        super().save(*args, **kwargs)


class SampleDisease(models.Model):
    sample_disease = models.IntegerField(verbose_name=_('Samples With Diseases'))
    product_disease = models.ForeignKey(ProductDisease, verbose_name=_('Disease'), on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Percentage'), null=True,
                                     blank=True)
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'),
                                          on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Sample Disease')
        verbose_name_plural = _('Sample Diseases')
        constraints = [
            models.UniqueConstraint(
                fields=['sample_collection', 'product_disease'],
                name='unique_sample_collection_product_disease'),
        ]

    def save(self, *args, **kwargs):
        total_sample_weight = SampleWeight.objects.filter(sample_collection=self.sample_collection).count()
        self.percentage = (self.sample_disease / total_sample_weight) * 100

        super().save(*args, **kwargs)


class SamplePhysicalDamage(models.Model):
    sample_physical_damage = models.IntegerField(verbose_name=_('Samples With Physical Damage'))
    product_physical_damage = models.ForeignKey(ProductPhysicalDamage, verbose_name=_('Physical Damage'),
                                                on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Percentage'), null=True,
                                     blank=True)
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'),
                                          on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Sample Physical Damage')
        verbose_name_plural = _('Sample Physical Damages')
        constraints = [
            models.UniqueConstraint(
                fields=['sample_collection', 'product_physical_damage'],
                name='unique_sample_collection_product_physical_damage'),
        ]

    def save(self, *args, **kwargs):
        total_sample_weight = SampleWeight.objects.filter(sample_collection=self.sample_collection).count()
        self.percentage = (self.sample_physical_damage / total_sample_weight) * 100

        super().save(*args, **kwargs)


class SampleResidue(models.Model):
    sample_residue = models.IntegerField(verbose_name=_('Samples With Residue'))
    product_residue = models.ForeignKey(ProductResidue, verbose_name=_('Residue'), on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Percentage'), null=True,
                                     blank=True)
    sample_collection = models.ForeignKey(SampleCollection, verbose_name=_('Sample Collection'),
                                          on_delete=models.CASCADE)

    def __str__(self):
        return f""

    class Meta:
        verbose_name = _('Sample Residue')
        verbose_name_plural = _('Sample Residue')
        constraints = [
            models.UniqueConstraint(
                fields=['sample_collection', 'product_residue'],
                name='unique_sample_collection_product_residue'),
        ]

    def save(self, *args, **kwargs):
        total_sample_weight = SampleWeight.objects.filter(sample_collection=self.sample_collection).count()
        self.percentage = (self.sample_residue / total_sample_weight) * 100

        super().save(*args, **kwargs)
