from django.urls import path
from . import views

app_name = 'lab'

urlpatterns = [
    path('', views.assay_select, name='assay_select'),
    path('assay/<int:assay_id>/upload/', views.upload_compounds, name='upload_compounds'),
    path('submit/confirm/', views.confirm_submission, name='confirm_submission'),
    path('requests/mine/', views.my_requests, name='my_requests'),
    path('dashboard/', views.assay_dashboard, name='assay_dashboard'),
    path('requests/<int:request_id>/update/', views.update_request_status, name='update_request_status'),
]
