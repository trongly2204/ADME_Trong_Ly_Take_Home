"""
Tests for the ADME Lab Portal.

These tests cover the existing functionality. When working on your TODO tasks,
add tests alongside your implementation.

Run with:
    python manage.py test lab
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import io

from .models import AssayType, TestRequest, Compound
from .utils import parse_compound_spreadsheet, SpreadsheetParseError


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class AssayTypeModelTest(TestCase):

    def setUp(self):
        self.assay = AssayType.objects.create(
            name='Human Liver Microsomal Stability',
            code='MET-HLM',
            category=AssayType.Category.METABOLIC_STABILITY,
            description='CYP-mediated metabolic stability assay.',
            turnaround_days=5,
        )

    def test_str_representation(self):
        self.assertEqual(str(self.assay), 'MET-HLM — Human Liver Microsomal Stability')

    def test_default_is_active(self):
        self.assertTrue(self.assay.is_active)


class TestRequestModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='researcher', password='testpass123')
        self.assay = AssayType.objects.create(
            name='PAMPA Permeability',
            code='PER-PAMPA',
            category=AssayType.Category.PERMEABILITY,
            description='Passive permeability assay.',
            turnaround_days=3,
        )
        self.request = TestRequest.objects.create(
            assay=self.assay,
            requested_by=self.user,
        )

    def test_default_status_is_pending(self):
        self.assertEqual(self.request.status, TestRequest.Status.PENDING)

    def test_compound_count_zero_initially(self):
        self.assertEqual(self.request.compound_count(), 0)

    def test_compound_count_with_compounds(self):
        Compound.objects.create(
            test_request=self.request,
            drug_name='Acetaminophen',
            batch_number='BN-001',
            container_barcode=1234567890,
        )
        Compound.objects.create(
            test_request=self.request,
            drug_name='Ibuprofen',
            batch_number='BN-002',
            container_barcode=9876543210,
        )
        self.assertEqual(self.request.compound_count(), 2)


# ---------------------------------------------------------------------------
# Utility tests
# ---------------------------------------------------------------------------

class ParseSpreadsheetTest(TestCase):

    def _make_xlsx(self, rows):
        """Create an in-memory .xlsx file from a list of row tuples."""
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        for row in rows:
            ws.append(row)
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf

    def test_parses_valid_spreadsheet(self):
        xlsx = self._make_xlsx([
            ('Drug Name', 'Batch Number', 'Container Barcode'),
            ('Acetaminophen', 'BN-001', 1000000001),
            ('Ibuprofen', 'BN-002', 1000000002),
        ])
        result = parse_compound_spreadsheet(xlsx)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['drug_name'], 'Acetaminophen')
        self.assertEqual(result[1]['container_barcode'], 1000000002)

    def test_raises_on_missing_columns(self):
        xlsx = self._make_xlsx([
            ('Drug Name', 'Batch Number'),  # missing Container Barcode
            ('Acetaminophen', 'BN-001'),
        ])
        with self.assertRaises(SpreadsheetParseError) as ctx:
            parse_compound_spreadsheet(xlsx)
        self.assertIn('container barcode', str(ctx.exception).lower())

    def test_skips_blank_rows(self):
        xlsx = self._make_xlsx([
            ('Drug Name', 'Batch Number', 'Container Barcode'),
            ('Acetaminophen', 'BN-001', 1000000001),
            (None, None, None),  # blank
            ('Ibuprofen', 'BN-002', 1000000002),
        ])
        result = parse_compound_spreadsheet(xlsx)
        self.assertEqual(len(result), 2)

    def test_raises_on_invalid_barcode(self):
        xlsx = self._make_xlsx([
            ('Drug Name', 'Batch Number', 'Container Barcode'),
            ('Acetaminophen', 'BN-001', 'NOT-A-NUMBER'),
        ])
        with self.assertRaises(SpreadsheetParseError) as ctx:
            parse_compound_spreadsheet(xlsx)
        self.assertIn('barcode', str(ctx.exception).lower())

    def test_case_insensitive_headers(self):
        xlsx = self._make_xlsx([
            ('DRUG NAME', 'BATCH NUMBER', 'CONTAINER BARCODE'),
            ('Metformin', 'BN-100', 5000000001),
        ])
        result = parse_compound_spreadsheet(xlsx)
        self.assertEqual(result[0]['drug_name'], 'Metformin')

    def test_raises_on_duplicate_barcodes(self):
        xlsx = self._make_xlsx([
            ('Drug Name', 'Batch Number', 'Container Barcode'),
            ('Acetaminophen', 'BN-001', 11111111),
            ('Ibuprofen', 'BN-002', 11111111),  # duplicate barcode
        ])
        with self.assertRaises(SpreadsheetParseError) as ctx:
            parse_compound_spreadsheet(xlsx)
        self.assertIn('duplicate', str(ctx.exception).lower())
        self.assertIn('11111111', str(ctx.exception))

    def test_unique_barcodes_does_not_raise(self):
        xlsx = self._make_xlsx([
            ('Drug Name', 'Batch Number', 'Container Barcode'),
            ('Acetaminophen', 'BN-001', 1000000001),
            ('Ibuprofen', 'BN-002', 1000000002),
            ('Metformin', 'BN-003', 1000000003),
        ])
        result = parse_compound_spreadsheet(xlsx)
        self.assertEqual(len(result), 3)


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class AssaySelectViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user1', password='testpass123')
        self.assay = AssayType.objects.create(
            name='Kinetic Aqueous Solubility',
            code='SOL-NEP',
            category=AssayType.Category.SOLUBILITY,
            description='Nephelometry solubility assay.',
            turnaround_days=3,
        )

    def test_redirects_unauthenticated_user(self):
        response = self.client.get(reverse('lab:assay_select'))
        self.assertRedirects(response, '/accounts/login/?next=/')

    def test_authenticated_user_sees_assay_list(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('lab:assay_select'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SOL-NEP')

    def test_post_valid_assay_redirects_to_upload(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('lab:assay_select'), {'assay': self.assay.pk})
        self.assertRedirects(response, reverse('lab:upload_compounds', args=[self.assay.pk]))


class AssayDashboardViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.scientist = User.objects.create_user(username='scientist', password='testpass123')
        self.researcher = User.objects.create_user(username='researcher', password='testpass123')
        self.assay = AssayType.objects.create(
            name='Caco-2 Permeability',
            code='PER-CACO2',
            category=AssayType.Category.PERMEABILITY,
            description='Caco-2 bidirectional assay.',
            turnaround_days=7,
        )

    def test_dashboard_shows_all_users_requests(self):
        """The dashboard must show requests from ALL users, not just the logged-in one."""
        TestRequest.objects.create(assay=self.assay, requested_by=self.researcher)
        self.client.login(username='scientist', password='testpass123')
        response = self.client.get(reverse('lab:assay_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'researcher')

    def test_status_update_changes_status(self):
        tr = TestRequest.objects.create(assay=self.assay, requested_by=self.researcher)
        self.assertEqual(tr.status, TestRequest.Status.PENDING)

        self.client.login(username='scientist', password='testpass123')
        self.client.post(
            reverse('lab:update_request_status', args=[tr.pk]),
            {'status': TestRequest.Status.IN_PROGRESS, 'notes': 'Started today'},
        )
        self.client.post(
            reverse('lab:update_request_status', args=[tr.pk]),
            {'status': TestRequest.Status.IN_PROGRESS, 'priority': TestRequest.Priority.NORMAL, 'notes': 'Started today'},
        )
        tr.refresh_from_db()
        self.assertEqual(tr.status, TestRequest.Status.IN_PROGRESS)
        self.assertEqual(tr.notes, 'Started today')
    def test_filter_by_status_returns_only_matching_requests(self):
        pending_req = TestRequest.objects.create(assay=self.assay, requested_by=self.researcher)
        complete_req = TestRequest.objects.create(
            assay=self.assay, requested_by=self.researcher, status=TestRequest.Status.COMPLETE
        )
        self.client.login(username='scientist', password='testpass123')
        response = self.client.get(reverse('lab:assay_dashboard') + '?status=PENDING')
        requests_in_context = list(response.context['all_requests'])
        self.assertIn(pending_req, requests_in_context)
        self.assertNotIn(complete_req, requests_in_context)
    