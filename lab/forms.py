from django import forms
from .models import TestRequest, AssayType


class AssaySelectForm(forms.Form):
    """Step 1: choose which assay to request."""

    assay = forms.ModelChoiceField(
        queryset=AssayType.objects.filter(is_active=True),
        empty_label="— Select an assay —",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
        label="Laboratory Assay",
    )


class CompoundUploadForm(forms.Form):
    """Step 2: upload an Excel spreadsheet of compounds."""

    spreadsheet = forms.FileField(
        label="Compound list (Excel .xlsx)",
        help_text="Upload an .xlsx file with columns: Drug Name, Batch Number, Container Barcode",
        widget=forms.FileInput(attrs={'accept': '.xlsx', 'class': 'form-control'}),
    )
    notes = forms.CharField(
        required=False,
        label="Additional notes",
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control',
                                     'placeholder': 'Any special instructions for the lab…'}),
    )

    def clean_spreadsheet(self):
        f = self.cleaned_data['spreadsheet']
        if not f.name.endswith('.xlsx'):
            raise forms.ValidationError("Only .xlsx files are accepted.")
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File too large (max 5 MB).")
        return f


class StatusUpdateForm(forms.ModelForm):
    """Inline form for lab scientists to update test request status."""

    class Meta:
        model = TestRequest
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control form-control-sm'}),
        }
