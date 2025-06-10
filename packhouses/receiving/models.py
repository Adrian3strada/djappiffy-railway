from django.db import models, transaction
from organizations.models import Organization
from django.utils.translation import gettext_lazy as _
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import get_processing_status_choices, get_batch_status_change
from packhouses.catalogs.models import (WeighingScale, Supply, HarvestingCrew, Provider, ProductFoodSafetyProcess,
                                        Product, Vehicle, ProductPest, ProductDisease, ProductPhysicalDamage,
                                        OrchardCertification,
                                        ProductResidue, ProductDryMatterAcceptanceReport, Orchard, Market)
from common.base.models import Pest
from django.db.models import F, Sum
from django.core.exceptions import ValidationError
from common.settings import STATUS_CHOICES


# Create your models here.
class Batch(models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_('Batch Number'), null=True, blank=True)
    status = models.CharField(max_length=25, verbose_name=_('Status'),
                                     choices=STATUS_CHOICES, default='open', blank=True)
    is_available_for_processing = models.BooleanField(default=False, verbose_name=_('Available for Processing'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Entry Date'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'),)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children', verbose_name=_('Parent'))

    def __str__(self):
        incoming = getattr(self, 'incomingproduct', None)

        if incoming:
            sh = getattr(incoming, 'scheduleharvest', None)
            harvest = f"{_('Schedule Harvest Number')}: {sh.ooid}" if sh else _('No Harvest')
            return f"Batch {self.ooid} – {_('Incoming Product')} ID: {incoming.id} – {harvest}"

        if hasattr(self, 'children') and self.children.exists():
            return f"{self.ooid} – {_('Parent Batch')}"

        return f"{self.ooid} – {_('No Incoming Product Associated')}"

    @property
    def ingress_weight(self):
        if self.batchweightmovement_set.exists():
            return self.batchweightmovement_set.aggregate(
                batch_weight=Sum('weight')
            )['batch_weight']
        return 0

    @property
    def weight_received(self):
        qs = self.batchweightmovement_set.filter(source__model__icontains='weighingset')
        total_weight = qs.aggregate(ingress_weight=Sum('weight'))['ingress_weight'] or 0
        if self.is_parent:
            total_weight += sum(child.ingress_weight for child in self.children.all())
        return total_weight

    @property
    def available_weight(self):
        total_weight = self.ingress_weight
        if self.is_parent:
            total_weight += sum(child.ingress_weight for child in self.children.all())
        return total_weight
    
    # Peso recibido propio (sin hijos), para el admin
    @property
    def self_weighing_weight(self):
        return self.batchweightmovement_set.filter(
            source__model__icontains='weighingset'
        ).aggregate(total=Sum('weight'))['total'] or 0

    # Peso disponible propio (sin hijos), para el admin
    @property
    def self_available_weight(self):
        return self.batchweightmovement_set.aggregate(
            total=Sum('weight')
        )['total'] or 0

    @property
    def yield_orchard_producer(self):
        return self.incomingproduct.scheduleharvest.orchard.producer

    @property
    def harvest_product_provider(self):
        return self.incomingproduct.scheduleharvest.product_provider

    @property
    def yield_harvest_gatherer(self):
        return self.incomingproduct.scheduleharvest.gatherer

    @property
    def yield_orchard(self):
        return self.incomingproduct.scheduleharvest.orchard

    @property
    def yield_orchard_registry_code(self):
        return self.incomingproduct.scheduleharvest.orchard.code

    @property
    def yield_orchard_selected_certifications(self):
        return self.incomingproduct.scheduleharvest.orchard_certifications.all()

    @property
    def yield_orchard_current_certifications(self):
        return OrchardCertification.objects.filter(
            orchard=self.yield_orchard,
            expiration_date__gte=self.created_at,
        )

    @property
    def yield_progress(self):
        return 0

    @property
    def yield_harvest_date(self):
        return self.incomingproduct.scheduleharvest.harvest_date

    @property
    def yield_producer(self):
        return self.incomingproduct.scheduleharvest.orchard.producer

    # @property para lotes padres e hijos
    @property
    def is_child(self):
        return self.parent is not None

    @property
    def is_parent(self):
        return self.children.exists()

    @property
    def children_list(self):
        return [child.ooid for child in self.children.all()]

    @property
    def children_ooids(self):
        return ", ".join(str(batch.ooid) for batch in self.children.all())

    @property
    def parent_batch_ooid(self):
        return self.parent.ooid if self.parent else ''


    def clean(self):
        if self.status == 'open':
            if self.is_available_for_processing:
                raise ValidationError(_("An 'open' batch cannot be available for processing."))
        # Verificar 'is_available_for_processing' se encuentre False en estado cerrado o cancelado
        if self.status in ['closed', 'canceled'] and self.pk:
            errors = {}
            if self.is_available_for_processing:
                errors['is_available_for_processing'] = _('Must be false when status is closed or canceled.')
            if errors:
                raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.ooid is None:
            with transaction.atomic():
                last = (
                    Batch.objects
                    .filter(organization=self.organization)
                    .order_by('-ooid')
                    .first()
                )
                self.ooid = (last.ooid + 1) if last else 1
        super().save(*args, **kwargs)

    # Métodos para historial de status del lote
    def status_history(self):
        return self.batchstatuschange_set.filter(field_name='status')

    def last_status_change(self):
        return self.status_history().order_by('-created_at').first()

    # Validar lotes para crear un padre
    @classmethod
    def validate_merge_batches(cls, batches_queryset):
        # Validar que los lotes seleccionados no sean hijos
        if batches_queryset.filter(parent__isnull=False).exists():
            raise ValidationError(
                _('You cannot merge batches that have already been merged into another batch.'),
                code='invalid_merge'
            )

        # Validar que ningun lote seleccionado sea padre
        if batches_queryset.filter(parent__isnull=True, children__isnull=False).exists():
            raise ValidationError(
                _('You cannot merge batches that already contain other merged batches.'),
                code='invalid_merge'
            )

        # Validar que los lotes seleccionados tenga en su status "ready"
        if batches_queryset.exclude(status='ready').exists():
            raise ValidationError(
                _('Only batches with a Review Status of “Ready” can be merged.'),
                code='invalid_status'
            )

        # Verificar que los lotes sean del mismo proveedor, producto, variedad, fenología
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

        # Verificar que los lotes a unir, sus mercados permitan mezclarse
        market_ids = batches_queryset.values_list('incomingproduct__scheduleharvest__market', flat=True).distinct()
        markets = Market.objects.filter(pk__in=market_ids)
        non_mixable_markets = markets.filter(is_mixable=False)

        if markets.count() > 1 and non_mixable_markets.exists():
            raise ValidationError(
                _('Cannot merge batches: non-mixable markets cannot be mixed with others.'),
                code='invalid_market_mix'
            )
    # Unir lotes para crear un padre
    @classmethod
    def merge_batches(cls, batches_queryset):
        cls.validate_merge_batches(batches_queryset)

        with transaction.atomic():
            # Elegir el lote con el ooid más grande como padre
            parent_batch = batches_queryset.order_by('-ooid').first()

            # Asignar a los demás como hijos
            for batch in batches_queryset:
                if batch != parent_batch:
                    batch.parent = parent_batch
                    batch.save(update_fields=['parent'])

            return parent_batch

    # Validar para unir un lote (no hijo) a un lote padre
    @classmethod
    def validate_add_batches_to_existing_merge(cls, parent, candidate_batches):
        # Verificar que el lote padre no sea hijo
        if parent.parent is not None:
            raise ValidationError(
                _('The selected destination batch is already merged into another batch.'),
                code='invalid_target'
            )
        # Verificar que los lotes seleccionados no sean hijos de otro lote que no sea el lote padre que se seleccione
        already_merged = candidate_batches.filter(parent__isnull=False)
        if already_merged.exists():
            oids = ", ".join(f'batch {o}' for o in already_merged.values_list("ooid", flat=True))
            raise ValidationError(
                _('The following batches are already part of another merged batch: %s') % oids,
                code='invalid_merge'
            )
        # Validar que los lotes seleccionados tenga en su status "ready"
        if candidate_batches.exclude(status='ready').exists():
            raise ValidationError(
                _('Only batches with a Review Status of “Ready” can be merged.'),
                code='invalid_status'
            )
        # Se añaden los lotes seleccionados a los hijos actuales del lote padre
        child_ids = list(parent.children.values_list('pk', flat=True))
        candidate_ids = list(candidate_batches.values_list('pk', flat=True))
        combined_ids = child_ids + candidate_ids

        all_batches = Batch.objects.filter(pk__in=combined_ids)

        # Verificar que los lotes sean del mismo proveedor, producto, variedad, fenología
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

        # Verificar que los lotes a unir, sus mercados permitan mezclarse
        market_ids = all_batches.values_list(
            'incomingproduct__scheduleharvest__market', flat=True
        ).distinct()
        markets = Market.objects.filter(pk__in=market_ids)

        # 2. Identificar los no mezclables
        non_mixable = markets.filter(is_mixable=False)

        # 3. Si hay más de un mercado total Y al menos un mercado no mezclable, hay que verificar si son del mismo
        if non_mixable.exists() and market_ids.count() > 1:
            non_mixable_ids = list(non_mixable.values_list('id', flat=True))

            if len(non_mixable_ids) > 1:
                raise ValidationError(
                    _('Cannot add batches: more than one non-mixable market is involved.'),
                    code='invalid_market_mix'
                )

            # También inválido si hay mezcla de ese mercado no mezclable con otros mezclables
            if markets.count() > 1:
                raise ValidationError(
                    _('Cannot add batches: non-mixable market cannot be mixed with others.'),
                    code='invalid_market_mix'
                )
    
    # Unir lote a un lote padre
    @classmethod
    def add_batches_to_merge(cls, parent, children_queryset):
        with transaction.atomic():
            for batch in children_queryset:
                batch.parent = parent
                batch.status = 'ready'
                batch.is_available_for_processing = False
                batch.save(update_fields=['parent', 'status', 'is_available_for_processing'])

    @classmethod
    def unmerge_all_children(cls, parent_batch):
        if not parent_batch.is_parent:
            raise ValidationError(
                _('The selected batch is not a parent.'), code='not_parent_batch')
        parent_batch.children.update(parent=None)

    @classmethod 
    def unmerge_selected_children(cls, batch_queryset):
        if not batch_queryset:
            raise ValidationError(_('No batches provided.'), code='no_batches_selected')

        non_children = [batch.ooid for batch in batch_queryset if batch.parent_id is None]
        if non_children:
            raise ValidationError(
                _('One or more selected batches are not linked to a parent batch.'),
                code='not_a_child_batch',
                params={'ooids': ', '.join(map(str, non_children))}
            )
        
        parents = {batch.parent_id for batch in batch_queryset}
        if len(parents) > 1:
            raise ValidationError(
                _('Selected batches belong to a different parent batch.'), 
                code='multiple_parent_batches'
                )
        batch_queryset.update(parent=None)

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
    source = models.JSONField(default=dict, blank=True, verbose_name=_("Source Information"))

    def __str__(self):
        return f"{self.batch} {self.created_at} :: {self.weight}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Batch Weight Movement')
        verbose_name_plural = _('Batch Weight Movements')

    def clean(self):
        if self.weight < 0 and self.batch.ingress_weight + self.weight < 0:
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
    status = models.CharField(max_length=20, verbose_name=_('Status'), choices=STATUS_CHOICES,
                              default='open')
    public_weighing_scale = models.ForeignKey(WeighingScale, verbose_name=_("Public Weighing Scale"),
                                              on_delete=models.PROTECT, null=True, blank=False)
    public_weight_result = models.FloatField(default=0, verbose_name=_("Public Weight Result"), )
    weighing_record_number = models.CharField(max_length=30, verbose_name=_('Weighing Record Number'), )
    total_weighed_sets = models.PositiveIntegerField(default=0, verbose_name=_('Total Weighed Sets'))
    mrl = models.FloatField(default=0, verbose_name=_('Maximum Residue Limit'), null=True, blank=True)
    phytosanitary_certificate = models.CharField(max_length=50, verbose_name=_('Phytosanitary Certificate'), null=True,
                                                 blank=True)
    kg_sample = models.FloatField(default=0, verbose_name=_("Kg for Sample"), validators=[MinValueValidator(0.01)])
    is_quarantined = models.BooleanField(default=False, verbose_name=_('In quarantine'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'))
    batch = models.OneToOneField(Batch, on_delete=models.PROTECT, verbose_name=_('Batch'), null=True, blank=True)
    comments = models.TextField(verbose_name=_("Comments"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def weighed_sets_count(self):
        return self.weighingset_set.count()

    @property
    def containers_count(self):
        return sum(
            container.quantity or 0
            for weighing in self.weighingset_set.all()
            for container in weighing.weighingsetcontainer_set.all()
        )

    @property
    def total_net_weight(self):
        return sum(
            weighing.net_weight or 0
            for weighing in self.weighingset_set.all()
        )

    @property
    def average_weight_per_container(self):
        total_weight = self.total_net_weight
        total_containers = self.containers_count
        return round(total_weight / total_containers, 3) if total_containers else 0.0

    @property
    def assigned_container_total(self):
        return sum(
            container.quantity or 0
            for vehicle in self.scheduleharvest.scheduleharvestvehicle_set.all()
            for container in vehicle.scheduleharvestcontainervehicle_set.all()
        )

    @property
    def full_container_total(self):
        return sum(
            container.full_containers or 0
            for vehicle in self.scheduleharvest.scheduleharvestvehicle_set.filter(has_arrived=True)
            for container in vehicle.scheduleharvestcontainervehicle_set.all()
        )

    @property
    def empty_container_total(self):
        return sum(
            container.empty_containers or 0
            for vehicle in self.scheduleharvest.scheduleharvestvehicle_set.filter(has_arrived=True)
            for container in vehicle.scheduleharvestcontainervehicle_set.all()
        )

    @property
    def missing_container_total(self):
        return sum(
            container.missing_containers or 0
            for vehicle in self.scheduleharvest.scheduleharvestvehicle_set.filter(has_arrived=True)
            for container in vehicle.scheduleharvestcontainervehicle_set.all()
        )


    def clean(self):
        if self.status == 'ready':
            if self.is_quarantined:
                raise ValidationError(_("Cannot be in quarantine if its status is 'ready'"))

        if self.pk:
            initial_status = IncomingProduct.objects.get(pk=self.pk).status
            if initial_status == 'ready' and self.status != 'ready':
                raise ValidationError("Once it is 'Ready', the status cannot be changed.")

        # Comentado porque model.clean() corre antes de validar/guardar inlines y weighingset_set siempre esta vacío al crear por primera vez
        # if self.status == "ready" and not self.weighingset_set.exists():
        #     raise ValidationError("At least one Weighing Set must be registered for the Incoming Product.")

    def save(self, *args, **kwargs):
        self.clean()

        previous_status = 'open'
        if self.pk:
            previous_status = IncomingProduct.objects.get(pk=self.pk).status

        if self.pk is not None:
            self.recalculate_weighing_data()
        super().save(*args, **kwargs)

        # Crear lote y movimientos
        if self.status == 'ready' and previous_status != 'ready' and self.batch_id is None:
            with transaction.atomic():
                new_batch = Batch.objects.create(
                    status='open',
                    is_available_for_processing=False,
                    organization=self.organization
                )
                self.batch = new_batch
                super().save(update_fields=['batch'])

                for weighing_set in self.weighingset_set.all():
                    exists = BatchWeightMovement.objects.filter(
                        batch=new_batch,
                        source__model=weighing_set.__class__.__name__,
                        source__id=weighing_set.pk
                    ).exists()
                    if not exists:
                        BatchWeightMovement.objects.create(
                            batch=new_batch,
                            weight=weighing_set.net_weight or 0,
                            source={
                                "model": weighing_set.__class__.__name__,
                                "id": weighing_set.pk,
                                "gross_weight": weighing_set.gross_weight,
                                "container_tare": weighing_set.container_tare,
                                "platform_tare": weighing_set.platform_tare
                            }
                        )

    def recalculate_weighing_data(self):
        weighing_sets = self.weighingset_set.all()
        self.total_weighed_sets = weighing_sets.count()

        self.total_weighed_set_containers = sum(
            container.quantity or 0
            for set in weighing_sets
            for container in set.weighingsetcontainer_set.all()
        )
        self.packhouse_weight_result = weighing_sets.aggregate(
            total=Sum('net_weight')
        )['total'] or 0.0
        if self.total_weighed_set_containers > 0:
            self.average_per_container = round(
                self.total_weighed_set_containers / self.total_weighed_set_containers, 3
            )
        else:
            self.average_per_container = 0.0


    def __str__(self):
        schedule_harvest = self.scheduleharvest
        if schedule_harvest:
            return f"{schedule_harvest.ooid} - {schedule_harvest.orchard}"
        return self.id

    class Meta:
        verbose_name = _('Incoming Product')
        verbose_name_plural = _('Incoming Product')


class WeighingSet(models.Model):
    ooid = models.PositiveIntegerField(verbose_name=_("ID"), null=True, blank=True)
    harvesting_crew = models.ForeignKey(HarvestingCrew, verbose_name=_("Harvesting Crew"), on_delete=models.CASCADE, )
    gross_weight = models.FloatField(default=0.0, verbose_name=_("Gross Weight"), )
    total_containers = models.PositiveIntegerField(default=0, verbose_name=_('Total Containments'))
    container_tare = models.FloatField(default=0.0, verbose_name=_("Container Tare"), )
    platform_tare = models.FloatField(default=0.0, verbose_name=_("Platform Tare"), )
    net_weight = models.FloatField(default=0.0, verbose_name=_("Net Weight"), )
    protected = models.BooleanField(default=False, verbose_name=_("Protected"))
    incoming_product = models.ForeignKey(IncomingProduct, verbose_name=_('Incoming Product'), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.ooid}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            type(self).objects.exclude(pk=self.pk).filter(
                incoming_product=self.incoming_product
            ).update(protected=True)

            self.protected = False

            # Asignar un ooid incremental
            last_record = (
                type(self).objects
                .filter(incoming_product=self.incoming_product)
                .select_for_update()
                .order_by('-ooid')
                .first()
            )
            self.ooid = (last_record.ooid + 1) if last_record else 1
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.protected:
            raise ValidationError(_("Only the latest (unprotected) weighing set can be deleted; older sets remain locked."))
        incoming_product_temp = self.incoming_product
        deleted_ooid = self.ooid

        with transaction.atomic():
            super().delete(*args, **kwargs)
            updated_count = type(self).objects.filter(
                incoming_product=incoming_product_temp,
                ooid__gt=deleted_ooid
            ).update(ooid=F('ooid') - 1)

class WeighingSetContainer(models.Model):
    harvest_container = models.ForeignKey(Supply, on_delete=models.CASCADE,
                                          limit_choices_to={'kind__category': 'harvest_container'},
                                          verbose_name=_('Harvest Containments'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    weighing_set = models.ForeignKey(WeighingSet, verbose_name=_('Incoming Product'), on_delete=models.CASCADE,
                                     null=True, blank=True)

    def clean(self):
        if not self.pk:
            return 

        if self.weighing_set and self.weighing_set.protected:
            try:
                old = WeighingSetContainer.objects.get(pk=self.pk)
            except WeighingSetContainer.DoesNotExist:
                return
            changed = any(
                getattr(self, field.name) != getattr(old, field.name)
                for field in self._meta.fields
                if field.name not in ['id',]
            )

            if changed:
                raise ValidationError(_("You cannot modify a container that belongs to a protected weighing set."))

    
    def delete(self, *args, **kwargs):
        if self.weighing_set and self.weighing_set.protected:
            raise ValidationError(_('You cannot delete a container that belongs to a protected weighing set.'))
        return super().delete(*args, **kwargs)
    
    class Meta:
        verbose_name = _('Weighing Set Containment')
        verbose_name_plural = _('Weighing Sets Containments')


class FoodSafety(models.Model):
    batch = models.OneToOneField(Batch, verbose_name=_('Batch'), on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Organization'), )
    status = models.CharField(max_length=20, verbose_name=_('Status'), choices=STATUS_CHOICES, default='open', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
