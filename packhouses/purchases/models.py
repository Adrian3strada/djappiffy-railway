from django.db import models, transaction
from common.profiles.models import UserProfile
from common.mixins import (CleanKindAndOrganizationMixin, CleanNameAndOrganizationMixin, CleanProductMixin,
                           CleanNameOrAliasAndOrganizationMixin, CleanNameAndMarketMixin, CleanNameAndProductMixin,
                           CleanNameAndProviderMixin, CleanNameAndCategoryAndOrganizationMixin,
                           CleanProductVarietyMixin, CleanNameAndAliasProductMixin,
                           CleanNameAndCodeAndOrganizationMixin,
                           CleanNameAndVarietyAndMarketAndVolumeKindMixin, CleanNameAndMaquiladoraMixin)
from organizations.models import Organization
from cities_light.models import City, Country, Region, SubRegion
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from common.base.models import ProductKind, CapitalFramework, LegalEntityCategory, Currency, SupplyMeasureUnitCategory, FruitPurchasePriceCategory
from packhouses.packhouse_settings.models import (Bank, VehicleOwnershipKind,
                                                  PaymentKind, VehicleFuelKind, VehicleKind, VehicleBrand,
                                                  OrchardCertificationVerifier,
                                                  OrchardCertificationKind)
from packhouses.catalogs.models import Supply, Provider
from common.settings import STATUS_CHOICES
from django.contrib.auth import get_user_model
import datetime
User = get_user_model()
from common.base.settings import SUPPLY_MEASURE_UNIT_CATEGORY_CHOICES
from django.db.models import Sum
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from .settings import PURCHASE_SERVICE_CATEGORY_CHOICES, PURCHASE_CATEGORY_CHOICES, FRUIT_PURCHASE_CATEGORY_CHOICES, FRUIT_RECEIPT_KIND_CHOICES
from packhouses.receiving.models import Batch
from packhouses.catalogs.models import Service
from common.utils import validate_file_extension

# Create your models here.
class Requisition(models.Model):
    ooid = models.PositiveIntegerField(
        verbose_name=_("Folio"),
        null=True, blank=True, unique=True
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.PROTECT
    )
    comments = models.TextField(
        verbose_name=_("Comments"),
        null=True, blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default='open',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.ooid}"

    def save(self, *args, **kwargs):
        user = kwargs.pop('user_id', None)
        if not self.ooid:
            # Usar transacción y bloqueo de fila para evitar condiciones de carrera
            with transaction.atomic():
                last_order = Requisition.objects.select_for_update().filter(organization=self.organization).order_by(
                    '-ooid').first()
                self.ooid = (last_order.ooid + 1) if last_order and last_order.ooid is not None else 1

        if user:
            self.user = user

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Requisition")
        verbose_name_plural = _("Requisitions")
        ordering = ['-ooid']
        constraints = [
            models.UniqueConstraint(fields=['ooid', 'organization'], name='unique_ooid_organization')
        ]


class RequisitionSupply(models.Model):
    requisition = models.ForeignKey(
        Requisition,
        verbose_name=_("Requisition"),
        on_delete=models.CASCADE
    )
    supply = models.ForeignKey(
        Supply,
        verbose_name=_("Supply"),
        on_delete=models.PROTECT
    )
    quantity = models.DecimalField(
        verbose_name=_("Quantity"),
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    unit_category = models.ForeignKey(
        SupplyMeasureUnitCategory,
        verbose_name=_('Unit category'),
        on_delete=models.PROTECT
    )
    delivery_deadline = models.DateField(
        verbose_name=_('Delivery deadline'),
        default=datetime.date.today
    )
    comments = models.CharField(
        max_length=255,
        verbose_name=_("Comments"),
        null=True, blank=True
    )
    is_enabled = models.BooleanField(
        verbose_name=_("Is enabled"),
        default=True
    )

    def __str__(self):
        return f"(Req. {self.requisition.ooid}) - {self.supply}"

    class Meta:
        verbose_name = _("Requisition Supply")
        verbose_name_plural = _("Requisition Supplies")
        ordering = ['-requisition']


class PurchaseOrder(models.Model):
    """
    Modelo que representa una orden de compra de insumos.

    Controla no solo los datos de proveedor, moneda, impuestos y comentarios, sino también
    el control del folio único por organización (ooid), el balance de pago pendiente y el estado
    del flujo de compra (abierta, lista, cerrada o cancelada).

    Incluye métodos para calcular dinámicamente el balance contable, considerando insumos,
    impuestos, cargos, deducciones y pagos registrados.
    """

    ooid = models.PositiveIntegerField(
        verbose_name=_("Folio"),
        null=True, blank=True, unique=True
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.PROTECT
    )
    provider = models.ForeignKey(
        Provider,
        verbose_name=_("Provider"),
        on_delete=models.PROTECT
    )
    payment_date = models.DateField(
        verbose_name=_('Payment date'),
        default=datetime.date.today
    )
    currency = models.ForeignKey(
        Currency,
        verbose_name=_("Currency"),
        on_delete=models.PROTECT
    )
    tax = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name=_("Tax (%)"),
        null=True, blank=True
    )
    comments = models.TextField(
        verbose_name=_("Comments"),
        null=True, blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default='open',
    )
    total_cost = models.DecimalField(
        verbose_name=_("Total cost (with tax)"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    balance_payable = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0,
        verbose_name=_("Balance payable")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.PROTECT
    )

    def save(self, *args, **kwargs):
        """
        Guarda la orden de compra, asegurando la asignación de un folio único incremental (ooid)
        de manera transaccional por organización. Permite opcionalmente asociar un usuario
        mediante el parámetro `user_id`.
        """
        user = kwargs.pop('user_id', None)
        if not self.ooid:
            with transaction.atomic():
                last_order = PurchaseOrder.objects.select_for_update().filter(
                    organization=self.organization
                ).order_by('-ooid').first()
                self.ooid = (last_order.ooid + 1) if last_order and last_order.ooid is not None else 1

        if user:
            self.user = user

        super().save(*args, **kwargs)

    def simulate_balance(self):
        """
        Calcula el balance de pago simulado de la orden de compra:
        Suma de insumos, impuestos, cargos adicionales, deducciones aplicadas y pagos realizados (excluyendo cancelados).

        El cálculo es decimalmente preciso y devuelve un resumen detallado de cada componente.
        """
        supplies_total = self.purchaseordersupply_set.aggregate(
            total=models.Sum('total_price')
        )['total'] or Decimal('0.00')

        tax_percent = self.tax or Decimal('0.00')
        tax_decimal = tax_percent / Decimal('100.00')
        tax_amount = (supplies_total * tax_decimal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        payments_total = self.purchaseorderpayment_set.exclude(
            status='canceled'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        charges_total = self.purchaseordercharge_set.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        deductions_total = self.purchaseorderdeduction_set.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        # Cálculo del costo total
        total_cost = supplies_total + tax_amount + charges_total - deductions_total
        total_cost = total_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        balance = total_cost - payments_total
        balance = balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'balance': balance,
            'supplies_total': supplies_total,
            'tax_amount': tax_amount,
            'charges_total': charges_total,
            'deductions_total': deductions_total,
            'payments_total': payments_total,
            'total_cost': total_cost
        }

    def recalculate_balance(self, save=False, raise_exception=False):
        """
        Recalcula el balance real de la orden de compra y el costo total.

        Args:
            save (bool): Si es True, guarda el nuevo balance_payable y el total_cost en la base de datos.
            raise_exception (bool): Si es True y el balance resulta negativo, lanza ValidationError.

        Returns:
            dict: Resultado del cálculo simulado con detalle de totales.
        """
        data = self.simulate_balance()

        if data['balance'] < 0 and raise_exception:
            raise ValidationError(
                (f"Cannot save the order because the balance is negative (${data['balance']}). "
                 f"Please contact the Purchasing department.")
            )

        if save:
            self.balance_payable = data['balance']
            self.total_cost = data['total_cost']
            self.save(update_fields=['balance_payable', 'total_cost'])

        return data

    def __str__(self):
        """
        Representación legible de la orden de compra, usando el folio y el proveedor.
        """
        return f"{self.ooid} - {self.provider.name}"

    class Meta:
        verbose_name = _("Purchase Order")
        verbose_name_plural = _("Purchase Orders")
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['ooid', 'organization'], name='unique_ooid_purchase_order_organization')
        ]

class PurchaseOrderSupply(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        verbose_name=_("Purchase Order"),
        on_delete=models.CASCADE
    )
    requisition_supply = models.ForeignKey(
        RequisitionSupply,
        verbose_name=_("Supply"),
        on_delete=models.PROTECT
    )
    quantity = models.DecimalField(
        verbose_name=_("Quantity"),
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    unit_category = models.ForeignKey(
        SupplyMeasureUnitCategory,
        verbose_name=_('Unit category'),
        on_delete=models.PROTECT,
    )
    delivery_deadline = models.DateField(
        verbose_name=_('Delivery deadline'),
        default=datetime.date.today
    )
    unit_price = models.DecimalField(
        verbose_name=_("Unit Price"),
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    total_price = models.DecimalField(
        verbose_name=_("Total Price"),
        max_digits=12, decimal_places=2,
        editable=False
    )
    comments = models.CharField(
        max_length=255,
        verbose_name=_("Comments"),
        null=True, blank=True
    )
    is_in_inventory = models.BooleanField(
        default=False,
        verbose_name = _("Is in inventory")
    )

    def __str__(self):
        return f"{self.requisition_supply} - {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Supply")
        verbose_name_plural = _("Supplies")
        constraints = [
            models.UniqueConstraint(fields=['purchase_order', 'requisition_supply'], name='unique_purchase_order_supply')
        ]

class PurchaseOrderCharge(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        verbose_name=_("Purchase Order"),
        on_delete=models.CASCADE
    )
    charge = models.CharField(
        max_length=255,
        verbose_name=_("Charge description"),
    )
    amount = models.DecimalField(
        verbose_name=_("Amount"),
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    def __str__(self):
        return f"{self.charge} - ${self.amount}"

    class Meta:
        verbose_name = _("Charge")
        verbose_name_plural = _("Charges")
        constraints = [
            models.UniqueConstraint(fields=['purchase_order', 'charge'], name='unique_purchase_order_charge')
        ]

class PurchaseOrderDeduction(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        verbose_name=_("Purchase Order"),
        on_delete=models.CASCADE
    )
    deduction = models.CharField(
        max_length=255,
        verbose_name=_("Deduction description"),
    )
    amount = models.DecimalField(
        verbose_name=_("Amount"),
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    def __str__(self):
        return f"{self.deduction} - ${self.amount}"

    class Meta:
        verbose_name = _("Deduction")
        verbose_name_plural = _("Deductions")
        constraints = [
            models.UniqueConstraint(fields=['purchase_order', 'deduction'], name='unique_purchase_order_deduction')
        ]

class PurchaseOrderPayment(models.Model):

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        verbose_name=_("Purchase Order"),
        on_delete=models.CASCADE
    )
    payment_date = models.DateField(
        verbose_name=_('Payment date'),
        default=datetime.date.today
    )
    amount = models.DecimalField(
        verbose_name=_("Amount"),
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    payment_kind = models.ForeignKey(
        PaymentKind,
        verbose_name=_("Payment kind"),
        on_delete=models.PROTECT
    )
    bank = models.ForeignKey(
        Bank,
        verbose_name=_("Bank"),
        on_delete=models.PROTECT,
        null = True,
        blank = True
    )
    comments = models.CharField(
        max_length=255,
        verbose_name=_("Comments"),
        null=True, blank=True
    )
    additional_inputs = models.JSONField(
        verbose_name=_("Additional inputs"),
        null=True, blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default='closed',
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Added by"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="added_payments"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    canceled_by = models.ForeignKey(
        User,
        verbose_name=_("Canceled by"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="canceled_payments"
    )
    cancellation_date = models.DateTimeField(
        verbose_name=_("Cancellation date"),
        null=True, blank=True
    )
    mass_payment = models.ForeignKey(
        "PurchaseMassPayment",
        verbose_name=_("Mass payment"),
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    proof_of_payment = models.FileField(
        verbose_name=_("Proof of Payment"),
        upload_to='purchases/payments/proofs/',
        validators=[validate_file_extension],
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.payment_date} - ${self.amount}"


    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")


class ServiceOrder(models.Model):
    """
    Representa una orden de servicio contratada por la organización, vinculada a un proveedor,
    un servicio específico y opcionalmente a un lote de producción (batch).

    Attributes:
        category (str): Categoría del servicio (elegida de un listado predefinido).
        provider (Provider): Proveedor que ofrece el servicio.
        service (Service): Servicio contratado.
        start_date (date): Fecha de inicio del servicio.
        end_date (date): Fecha de finalización del servicio.
        batch (Batch, optional): Lote relacionado al servicio, si aplica.
        cost (Decimal): Costo total del servicio.
        tax (Decimal, optional): Porcentaje de impuestos aplicados.
        status (str): Estado de la orden ('open', 'closed', etc.).
        created_at (datetime): Fecha de creación de la orden.
        created_by (User, optional): Usuario que creó la orden.
        balance_payable (Decimal): Saldo pendiente de pago.
        organization (Organization): Organización a la que pertenece la orden.
    """
    ooid = models.PositiveIntegerField(
        verbose_name=_("Folio"),
        null=True, blank=True, unique=True
    )
    category = models.CharField(
        max_length=255,
        verbose_name=_("Category"),
        choices=PURCHASE_SERVICE_CATEGORY_CHOICES,
    )
    provider = models.ForeignKey(
        Provider,
        verbose_name=_("Provider"),
        on_delete=models.PROTECT
    )
    service = models.ForeignKey(
        Service,
        verbose_name=_("Service"),
        on_delete=models.PROTECT,
    )
    start_date = models.DateField(
        verbose_name=_('Start date'),
        default=datetime.date.today
    )
    end_date = models.DateField(
        verbose_name=_('End date'),
        default=datetime.date.today
    )
    batch = models.ForeignKey(
        Batch,
        verbose_name=_("Batch"),
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    payment_date = models.DateField(
        verbose_name=_('Payment date'),
        default=datetime.date.today
    )
    currency = models.ForeignKey(
        Currency,
        verbose_name=_("Currency"),
        on_delete=models.PROTECT
    )
    cost = models.DecimalField(
        verbose_name=_("Cost"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    tax = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Tax (%)"),
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name=_('Status')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Created by"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="created_services"
    )
    balance_payable = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("Balance payable")
    )
    total_cost = models.DecimalField(
        verbose_name=_("Total cost (with tax)"),
        max_digits=12,
        decimal_places=2,
        default=0
    )

    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.PROTECT
    )

    def simulate_balance(self):
        """
        Calcula el balance simulado de la orden de servicio, incluyendo:
        costo base, impuestos, cargos adicionales, deducciones y pagos realizados.
        """
        base_cost = self.cost or Decimal('0.00')
        tax_percent = self.tax or Decimal('0.00')
        tax_decimal = tax_percent / Decimal('100.00')
        tax_amount = (base_cost * tax_decimal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        charges_total = self.serviceordercharge_set.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        deductions_total = self.serviceorderdeduction_set.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        payments_total = self.serviceorderpayment_set.exclude(
            status='canceled'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        # Aquí se incluye el cálculo correcto del total_cost
        total_cost = base_cost + tax_amount + charges_total - deductions_total
        total_cost = total_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        balance = total_cost - payments_total
        balance = balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'base_cost': base_cost,
            'tax_amount': tax_amount,
            'charges_total': charges_total,
            'deductions_total': deductions_total,
            'payments_total': payments_total,
            'total_cost': total_cost,
            'balance': balance
        }

    def recalculate_balance(self, save=False, raise_exception=False):
        """
        Recalcula el balance real de la orden de servicio.

        Args:
            save (bool): Si True, guarda el nuevo balance.
            raise_exception (bool): Si True y el balance es negativo, lanza ValidationError.

        Returns:
            dict: Resultado detallado del cálculo del balance.
        """
        data = self.simulate_balance()

        if data['balance'] < 0 and raise_exception:
            raise ValidationError(
                (f"Cannot save the service order because the balance is negative (${data['balance']}).")
            )

        if save:
            self.balance_payable = data['balance']
            self.save(update_fields=['balance_payable'])

        return data

    class Meta:
        verbose_name = _("Service Order")
        verbose_name_plural = _("Service Orders")
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='check_end_date_greater_equal_start_date'
            )
        ]

    def save(self, *args, **kwargs):
        """
        Guarda la orden de servicio, asegurando la asignación de un folio único incremental (ooid)
        de manera transaccional por organización.
        """
        if not self.ooid:
            with transaction.atomic():
                last_order = ServiceOrder.objects.select_for_update().filter(
                    organization=self.organization
                ).order_by('-ooid').first()
                self.ooid = (last_order.ooid + 1) if last_order and last_order.ooid is not None else 1

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Returns:
            str: Nombre del servicio y su costo.
        """
        return f"Folio {self.ooid} - {self.provider.name} - {self.service.name} - ${self.balance_payable}"

class ServiceOrderCharge(models.Model):
    service_order = models.ForeignKey(
        ServiceOrder,
        verbose_name=_("Service Order"),
        on_delete=models.CASCADE
    )
    charge = models.CharField(
        max_length=255,
        verbose_name=_("Charge description"),
    )
    amount = models.DecimalField(
        verbose_name=_("Amount"),
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    def __str__(self):
        return f"{self.charge} - ${self.amount}"

    class Meta:
        verbose_name = _("Charge")
        verbose_name_plural = _("Charges")
        constraints = [
            models.UniqueConstraint(fields=['service_order', 'charge'], name='unique_service_order_charge')
        ]

class ServiceOrderDeduction(models.Model):
    service_order = models.ForeignKey(
        ServiceOrder,
        verbose_name=_("Service Order"),
        on_delete=models.CASCADE
    )
    deduction = models.CharField(
        max_length=255,
        verbose_name=_("Deduction description"),
    )
    amount = models.DecimalField(
        verbose_name=_("Amount"),
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    def __str__(self):
        return f"{self.deduction} - ${self.amount}"

    class Meta:
        verbose_name = _("Deduction")
        verbose_name_plural = _("Deductions")
        constraints = [
            models.UniqueConstraint(fields=['service_order', 'deduction'], name='unique_service_order_deduction')
        ]

class ServiceOrderPayment(models.Model):
    service_order = models.ForeignKey(
        ServiceOrder,
        verbose_name=_("Service Order"),
        on_delete=models.CASCADE
    )
    payment_date = models.DateField(
        verbose_name=_('Payment date'),
        default=datetime.date.today
    )
    amount = models.DecimalField(
        verbose_name=_("Amount"),
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    payment_kind = models.ForeignKey(
        PaymentKind,
        verbose_name=_("Payment kind"),
        on_delete=models.PROTECT
    )
    bank = models.ForeignKey(
        Bank,
        verbose_name=_("Bank"),
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    comments = models.CharField(
        max_length=255,
        verbose_name=_("Comments"),
        null=True, blank=True
    )
    additional_inputs = models.JSONField(
        verbose_name=_("Additional inputs"),
        null=True, blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default='closed',
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Added by"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="added_service_payments"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    canceled_by = models.ForeignKey(
        User,
        verbose_name=_("Canceled by"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="canceled_service_payments"
    )
    cancellation_date = models.DateTimeField(
        verbose_name=_("Cancellation date"),
        null=True, blank=True
    )
    mass_payment = models.ForeignKey(
        "PurchaseMassPayment",
        verbose_name=_("Mass payment"),
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    proof_of_payment = models.FileField(
        verbose_name=_("Proof of Payment"),
        upload_to='purchases/payments/proofs/',
        validators=[validate_file_extension],
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.payment_date} - ${self.amount}"

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")


class PurchaseMassPayment(models.Model):
    """
    Representa un pago masivo realizado a proveedores por órdenes de compra.

    Attributes:
        payment_date (date): Fecha del pago.
        amount (Decimal): Monto total del pago.
        payment_kind (PaymentKind): Tipo de pago utilizado.
        bank (Bank): Banco asociado al pago.
        comments (str): Comentarios adicionales sobre el pago.
        additional_inputs (JSONField): Campos adicionales para información extra.
        status (str): Estado del pago ('open', 'closed', etc.).
        created_by (User): Usuario que creó el registro.
        created_at (datetime): Fecha y hora de creación del registro.
    """
    ooid = models.PositiveIntegerField(
        verbose_name=_("Folio"),
        null=True, blank=True, unique=True
    )
    category = models.CharField(
        max_length=40,
        verbose_name=_("Category"),
        choices=PURCHASE_CATEGORY_CHOICES,
    )
    provider = models.ForeignKey(
        Provider,
        verbose_name=_("Provider"),
        on_delete=models.PROTECT
    )
    currency = models.ForeignKey(
        Currency,
        verbose_name=_("Currency"),
        on_delete=models.PROTECT
    )
    purchase_order = models.ManyToManyField(
        PurchaseOrder,
        verbose_name=_("Purchase Order"),
        related_name="purchase_mass_payments",
        blank=True
    )
    service_order = models.ManyToManyField(
        ServiceOrder,
        verbose_name=_("Service Order"),
        related_name="purchase_mass_payments",
        blank=True
    )
    payment_kind = models.ForeignKey(
        PaymentKind,
        verbose_name=_("Payment kind"),
        on_delete=models.PROTECT
    )
    additional_inputs = models.JSONField(
        verbose_name=_("Additional inputs"),
        null=True, blank=True
    )
    payment_date = models.DateField(
        verbose_name=_('Payment date'),
        default=datetime.date.today
    )
    amount = models.DecimalField(
        verbose_name=_("Amount"),
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    bank = models.ForeignKey(
        Bank,
        verbose_name=_("Bank"),
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    comments = models.CharField(
        max_length=255,
        verbose_name=_("Comments"),
        null=True, blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default='closed',
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Created by"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="added_mass_payments"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    canceled_by = models.ForeignKey(
        User,
        verbose_name=_("Canceled by"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="canceled_mass_payments"
    )
    cancellation_date = models.DateTimeField(
        verbose_name=_("Cancellation date"),
        null=True, blank=True
    )
    proof_of_payment = models.FileField(
        verbose_name=_("Proof of Payment"),
        upload_to='purchases/payments/proofs/',
        validators=[validate_file_extension],
        null=True,
        blank=True
    )
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.payment_date} - ${self.amount}"

    def recalculate_amount(self):
        """
        Recalcula el monto total del Mass Payment sumando el monto de los pagos aplicados.
        Si es de tipo 'purchase_order', suma los pagos realizados en esas órdenes.
        Si es de tipo 'service_order', suma los pagos realizados en esas órdenes.
        """
        if self.purchase_order.exists():
            # Si hay órdenes de compra, suma los pagos asociados
            payments = PurchaseOrderPayment.objects.filter(
                purchase_order__in=self.purchase_order.all(),
                status='closed',
                mass_payment=self
            )
            new_amount = sum(payment.amount for payment in payments)
        elif self.service_order.exists():
            # Si hay órdenes de servicio, suma los pagos asociados
            payments = ServiceOrderPayment.objects.filter(
                service_order__in=self.service_order.all(),
                status='closed',
                mass_payment=self
            )
            new_amount = sum(payment.amount for payment in payments)
        else:
            # Si no hay ni una ni otra, el monto se va a cero.
            new_amount = Decimal('0.00')

        # Actualizamos el monto en el Mass Payment
        self.amount = new_amount
        self.save(update_fields=["amount"])

    def save(self, *args, **kwargs):
        """
        Guarda la orden de servicio, asegurando la asignación de un folio único incremental (ooid)
        de manera transaccional por organización.
        """
        if not self.ooid:
            with transaction.atomic():
                last_order = PurchaseMassPayment.objects.select_for_update().filter(
                    organization=self.organization
                ).order_by('-ooid').first()
                self.ooid = (last_order.ooid + 1) if last_order and last_order.ooid is not None else 1

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Mass Payment")
        verbose_name_plural = _("Mass Payments")


class FruitPurchaseOrder(models.Model):
    """
    Representa una orden de compra de fruta, vinculada a un proveedor y a un lote específico.
    Permite registrar la cantidad de fruta comprada, su precio unitario y el costo total.
    """
    ooid = models.PositiveIntegerField(
        verbose_name=_("Folio"),
        null=True, blank=True, unique=True
    )
    batch = models.ForeignKey(
        Batch,
        verbose_name=_("Batch"),
        on_delete=models.PROTECT
    )
    category = models.CharField(
        max_length=40,
        verbose_name=_("Category"),
        choices=FRUIT_PURCHASE_CATEGORY_CHOICES,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Created by"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="created_fruit_orders"
    )
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{_('Order')} #{self.ooid} – {_('Batch')}: {self.batch.ooid}"

    def save(self, *args, **kwargs):
        if not self.ooid and self.organization:
            with transaction.atomic():
                last_order = FruitPurchaseOrder.objects.select_for_update().filter(
                    organization=self.organization
                ).order_by('-ooid').first()
                self.ooid = (last_order.ooid + 1) if last_order and last_order.ooid else 1

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Fruit Purchase Order")
        verbose_name_plural = _("Fruit Purchase Orders")
        ordering = ['-created_at', '-ooid']
        constraints = [
            models.UniqueConstraint(fields=['ooid', 'organization'], name='unique_ooid_per_organization'),
            models.UniqueConstraint(fields=['batch', 'organization'], name='unique_batch_fruit_order_organization')
        ]


class FruitPurchaseOrderReceipt(models.Model):
    """
    Representa un recibo de compra de fruta, vinculado a una orden de compra de fruta y a un proveedor/productor.
    Permite registrar el costo total y el estado del recibo.
    """
    ooid = models.PositiveIntegerField(
        verbose_name=_("Folio"),
        null=True, blank=True
    )
    fruit_purchase_order = models.ForeignKey(
        FruitPurchaseOrder,
        verbose_name=_("Fruit Purchase Order"),
        on_delete=models.CASCADE
    )
    receipt_kind = models.CharField(
        max_length=40,
        verbose_name=_("Receipt kind"),
        choices=FRUIT_RECEIPT_KIND_CHOICES,
    )
    provider = models.ForeignKey(
        Provider,
        verbose_name=_("Provider/Producer"),
        on_delete=models.PROTECT
    )
    price_category = models.ForeignKey(
        FruitPurchasePriceCategory,
        verbose_name=_("Price category"),
        on_delete=models.PROTECT
    )
    container_capacity = models.DecimalField(
        verbose_name=_("Container capacity"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)]
    )
    quantity = models.DecimalField(
        verbose_name=_("Quantity"),
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    unit_price = models.DecimalField(
        verbose_name=_("Unit Price"),
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    total_cost = models.DecimalField(
        verbose_name=_("Total cost"),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0.01)]
    )
    balance_payable = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0,
        verbose_name=_("Balance payable")
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default='open',
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Created by"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="created_fruit_receipts"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    canceled_by = models.ForeignKey(
        User,
        verbose_name=_("Canceled by"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="canceled_fruit_receipts"
    )
    cancellation_date = models.DateTimeField(
        verbose_name=_("Cancellation date"),
        null=True, blank=True
    )

    def __str__(self):
        return _("BATCH %(batch)s - RECEIPT %(receipt)s - %(provider)s") % {
            "batch": self.fruit_purchase_order.batch.ooid,
            "receipt": self.ooid,
            "provider": self.provider.name,
        }

    def recalculate_balance_payable(self):
        """
        Recalcula el balance_payable restando todos los pagos activos (no cancelados).
        """
        total_paid = FruitPurchaseOrderPayment.objects.filter(
            fruit_purchase_order_receipt=self,
            status__in=['open', 'closed']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        self.balance_payable = (self.quantity * self.unit_price) - total_paid
        self.balance_payable = self.balance_payable.quantize(Decimal('0.01'))

    def clean(self):
        if not self.fruit_purchase_order or not self.fruit_purchase_order.pk:
            return  # La orden aún no está guardada

        if not self.pk:
            return  # Este recibo aún no está guardado, no podemos validar pagos

        super().clean()

        if not self.quantity or not self.unit_price:
            return

        total_paid = FruitPurchaseOrderPayment.objects.filter(
            fruit_purchase_order_receipt=self,
            status__in=['open', 'closed']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        expected_total = self.quantity * self.unit_price
        new_balance = expected_total - total_paid

        if new_balance < 0:
            raise ValidationError({
                'balance_payable': _(
                    "The balance payable cannot be negative. "
                    "Total payments (%(paid)s) exceed the receipt total (%(total)s)."
                ) % {
                                       'paid': f"{total_paid:,.2f}",
                                       'total': f"{expected_total:,.2f}"
                                   }
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        user = kwargs.pop('user', None)

        with transaction.atomic():
            is_new = self.pk is None

            if user and is_new:
                self.created_by = user

            self.total_cost = self.quantity * self.unit_price

            if is_new:
                last_order = FruitPurchaseOrderReceipt.objects.select_for_update().filter(
                    fruit_purchase_order=self.fruit_purchase_order
                ).order_by('-ooid').first()
                self.ooid = (last_order.ooid + 1) if last_order and last_order.ooid is not None else 1

            super().save(*args, **kwargs)  # PRIMERO guarda la instancia

            # SOLO DESPUÉS de guardar, recalcula balance
            self.recalculate_balance_payable()
            super().save(update_fields=["balance_payable"])

    class Meta:
        verbose_name = _("Fruit Receipt")
        verbose_name_plural = _("Fruit Receipts")
        constraints = [
            models.UniqueConstraint(
                fields=['fruit_purchase_order', 'ooid'],
                name='unique_ooid_per_purchase_order'
            )
        ]


class FruitPurchaseOrderPayment(models.Model):
    fruit_purchase_order = models.ForeignKey(
        FruitPurchaseOrder,
        verbose_name=_("Fruit Purchase Order"),
        on_delete=models.CASCADE
    )
    fruit_purchase_order_receipt = models.ForeignKey(
        FruitPurchaseOrderReceipt,
        verbose_name=_("Fruit Purchase Order Receipt"),
        on_delete=models.CASCADE
    )
    payment_date = models.DateField(
        verbose_name=_('Payment date'),
        default=datetime.date.today
    )
    amount = models.DecimalField(
        verbose_name=_("Amount"),
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    payment_kind = models.ForeignKey(
        PaymentKind,
        verbose_name=_("Payment kind"),
        on_delete=models.PROTECT
    )
    bank = models.ForeignKey(
        Bank,
        verbose_name=_("Bank"),
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    comments = models.CharField(
        max_length=255,
        verbose_name=_("Comments"),
        null=True, blank=True
    )
    additional_inputs = models.JSONField(
        verbose_name=_("Additional inputs"),
        null=True, blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default='closed',
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Added by"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="added_fruit_payments"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    canceled_by = models.ForeignKey(
        User,
        verbose_name=_("Canceled by"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="canceled_fruit_payments"
    )
    cancellation_date = models.DateTimeField(
        verbose_name=_("Cancellation date"),
        null=True, blank=True
    )
    mass_payment = models.ForeignKey(
        "PurchaseMassPayment",
        verbose_name=_("Mass payment"),
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    proof_of_payment = models.FileField(
        verbose_name=_("Proof of Payment"),
        upload_to='purchases/payments/proofs/',
        validators=[validate_file_extension],
        null=True,
        blank=True
    )

    def clean(self):
        super().clean()

        if not self.fruit_purchase_order or not self.fruit_purchase_order.pk:
            return

        if not self.amount or not self.fruit_purchase_order_receipt:
            return

        payments_qs = FruitPurchaseOrderPayment.objects.filter(
            fruit_purchase_order_receipt=self.fruit_purchase_order_receipt
        ).exclude(status='canceled')

        if self.pk and self.status != 'canceled':
            payments_qs = payments_qs.exclude(pk=self.pk)

        total_paid = payments_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        if self.status != 'canceled':
            new_total = total_paid + self.amount
        else:
            new_total = total_paid

        total_receipt = self.fruit_purchase_order_receipt.quantity * self.fruit_purchase_order_receipt.unit_price

        if new_total > total_receipt:
            raise ValidationError({
                'amount': _(
                    "The total payment amount (%(new_total)s) exceeds the receipt total (%(receipt_total)s)."
                ) % {
                              'new_total': f"{new_total:,.2f}",
                              'receipt_total': f"{total_receipt:,.2f}"
                          }
            })

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        with transaction.atomic():
            if user and not self.pk:
                self.created_by = user
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_date} - ${self.amount}"

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
