from django.db import models
from django.contrib.auth.models import User


class AssayType(models.Model):
    """An in vitro ADME assay that the laboratory can perform."""

    class Category(models.TextChoices):
        SOLUBILITY = 'SOL', 'Solubility'
        PERMEABILITY = 'PER', 'Permeability'
        METABOLIC_STABILITY = 'MET', 'Metabolic Stability'
        PLASMA_PROTEIN_BINDING = 'PPB', 'Plasma Protein Binding'
        EFFLUX = 'EFX', 'Efflux'

    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=3, choices=Category.choices)
    description = models.TextField()
    turnaround_days = models.PositiveSmallIntegerField(
        help_text="Expected turnaround time in business days"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.code} — {self.name}"


class TestRequest(models.Model):
    """A user's request to run an assay on a batch of compounds."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETE = 'COMPLETE', 'Complete'
        ON_HOLD = 'ON_HOLD', 'On Hold'

    assay = models.ForeignKey(AssayType, on_delete=models.PROTECT, related_name='requests')
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='test_requests')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.assay.code} — {self.requested_by.username} — {self.created_at:%Y-%m-%d}"

    def compound_count(self):
        return self.compounds.count()


class Compound(models.Model):
    """A single drug compound entry uploaded as part of a TestRequest."""

    test_request = models.ForeignKey(TestRequest, on_delete=models.CASCADE, related_name='compounds')
    drug_name = models.CharField(max_length=200)
    batch_number = models.CharField(max_length=100)
    container_barcode = models.BigIntegerField()

    class Meta:
        ordering = ['drug_name']

    def __str__(self):
        return f"{self.drug_name} ({self.batch_number})"
