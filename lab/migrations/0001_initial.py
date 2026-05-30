from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssayType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('category', models.CharField(choices=[('SOL', 'Solubility'), ('PER', 'Permeability'), ('MET', 'Metabolic Stability'), ('PPB', 'Plasma Protein Binding'), ('EFX', 'Efflux')], max_length=3)),
                ('description', models.TextField()),
                ('turnaround_days', models.PositiveSmallIntegerField(help_text='Expected turnaround time in business days')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='TestRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETE', 'Complete'), ('ON_HOLD', 'On Hold')], default='PENDING', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assay', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='requests', to='lab.assaytype')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='test_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Compound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drug_name', models.CharField(max_length=200)),
                ('batch_number', models.CharField(max_length=100)),
                ('container_barcode', models.BigIntegerField()),
                ('test_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compounds', to='lab.testrequest')),
            ],
            options={
                'ordering': ['drug_name'],
            },
        ),
    ]
