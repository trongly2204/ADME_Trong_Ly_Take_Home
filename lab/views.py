from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .models import AssayType, TestRequest, Compound
from .forms import AssaySelectForm, CompoundUploadForm, StatusUpdateForm
from .utils import parse_compound_spreadsheet, SpreadsheetParseError


@login_required
def assay_select(request):
    """Step 1: user picks which assay they want to submit samples for."""
    if request.method == 'POST':
        form = AssaySelectForm(request.POST)
        if form.is_valid():
            assay_id = form.cleaned_data['assay'].pk
            return redirect('lab:upload_compounds', assay_id=assay_id)
    else:
        form = AssaySelectForm()

    assays = AssayType.objects.filter(is_active=True).order_by('category', 'name')
    return render(request, 'lab/assay_select.html', {'form': form, 'assays': assays})


@login_required
def upload_compounds(request, assay_id):
    """Step 2: user uploads an Excel spreadsheet of compounds."""
    assay = get_object_or_404(AssayType, pk=assay_id, is_active=True)

    if request.method == 'POST':
        form = CompoundUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                compounds = parse_compound_spreadsheet(request.FILES['spreadsheet'])
            except SpreadsheetParseError as exc:
                form.add_error('spreadsheet', str(exc))
            else:
                # Store parsed data in session for the confirmation step
                request.session['pending_compounds'] = compounds
                request.session['pending_assay_id'] = assay_id
                request.session['pending_notes'] = form.cleaned_data.get('notes', '')
                return redirect('lab:confirm_submission')
    else:
        form = CompoundUploadForm()

    return render(request, 'lab/upload_compounds.html', {'form': form, 'assay': assay})


@login_required
def confirm_submission(request):
    """Step 3: preview parsed compounds; confirm or cancel."""
    compounds = request.session.get('pending_compounds')
    assay_id = request.session.get('pending_assay_id')

    if not compounds or not assay_id:
        messages.warning(request, "No pending submission found. Please start again.")
        return redirect('lab:assay_select')

    assay = get_object_or_404(AssayType, pk=assay_id)

    if request.method == 'POST':
        if 'confirm' in request.POST:
            # Create the TestRequest and all Compound records
            test_request = TestRequest.objects.create(
                assay=assay,
                requested_by=request.user,
                notes=request.session.get('pending_notes', ''),
            )
            Compound.objects.bulk_create([
                Compound(test_request=test_request, **c) for c in compounds
            ])
            # Clear session
            for key in ('pending_compounds', 'pending_assay_id', 'pending_notes'):
                request.session.pop(key, None)

            messages.success(
                request,
                f"Request #{test_request.pk} submitted — {len(compounds)} compound(s) "
                f"queued for {assay.name}."
            )
            return redirect('lab:my_requests')
        else:
            # Cancel — clear session and start over
            for key in ('pending_compounds', 'pending_assay_id', 'pending_notes'):
                request.session.pop(key, None)
            return redirect('lab:assay_select')

    return render(request, 'lab/confirm_submission.html', {
        'assay': assay,
        'compounds': compounds,
    })


@login_required
def my_requests(request):
    """A researcher's own submission history."""
    requests_qs = (
        TestRequest.objects
        .filter(requested_by=request.user)
        .select_related('assay')
        .prefetch_related('compounds')
        .order_by('-created_at')
    )
    return render(request, 'lab/my_requests.html', {'test_requests': requests_qs})


@login_required
def assay_dashboard(request):
    """
    Scientist view: all requests aggregated across all users, grouped by assay.
    Allows inline status updates.
    """
    assays = (
        AssayType.objects
        .filter(is_active=True)
        .prefetch_related('requests__requested_by', 'requests__compounds')
        .annotate(request_count=Count('requests'))
        .order_by('category', 'name')
    )

    # Build a status form for each request (used in the template)
    status_forms = {}
    all_requests = TestRequest.objects.select_related('assay', 'requested_by').order_by('-created_at')
    for tr in all_requests:
        status_forms[tr.pk] = StatusUpdateForm(instance=tr)

    return render(request, 'lab/assay_dashboard.html', {
        'assays': assays,
        'all_requests': all_requests,
        'status_forms': status_forms,
    })


@login_required
def update_request_status(request, request_id):
    """POST-only: lab scientist updates status of a single TestRequest."""
    test_request = get_object_or_404(TestRequest, pk=request_id)
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=test_request)
        if form.is_valid():
            form.save()
            messages.success(request, f"Request #{test_request.pk} updated to {test_request.get_status_display()}.")
        else:
            messages.error(request, "Could not save status update — check form errors.")
    return redirect('lab:assay_dashboard')
