from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('dashboard/', views.pharmacist_dashboard, name='pharmacist_dashboard'),
    path('', views.public_pharmacy_list, name='public_list'),
    path('medicines/', views.MedicineListView.as_view(), name='medicine_list'),
    path('medicines/add/', views.MedicineCreateView.as_view(), name='medicine_add'),
    path('medicines/<int:pk>/edit/', views.MedicineUpdateView.as_view(), name='medicine_edit'),
    path('medicines/<int:pk>/delete/', views.MedicineDeleteView.as_view(), name='medicine_delete'),
    path('medicines/<int:pk>/stock/', views.update_stock, name='update_stock'),
    path('billing/', views.billing_pos, name='billing_pos'),
    
    # E-Commerce URLs
    path('cart/add/<int:medicine_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.unified_checkout, name='checkout'),
    path('history/', views.expenditure_history, name='expenditure_history'),
    path('bill/<int:bill_id>/', views.unified_bill_detail, name='unified_bill_detail'),
    path('bill/<int:bill_id>/pay/', views.pay_unified_bill, name='pay_unified_bill'),
]
