from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Medicine, PharmacyBill, PharmacyBillItem

def is_pharmacist(user):
    return user.is_authenticated and user.is_pharmacist

@login_required
def pharmacist_dashboard(request):
    if not is_pharmacist(request.user):
        messages.error(request, "Access denied. You are not a pharmacist.")
        return redirect('core:home')
    
    total_medicines = Medicine.objects.count()
    total_bills = PharmacyBill.objects.count()
    recent_bills = PharmacyBill.objects.order_by('-date')[:5]
    low_stock = Medicine.objects.filter(stock_quantity__lt=10)

    context = {
        'total_medicines': total_medicines,
        'total_bills': total_bills,
        'recent_bills': recent_bills,
        'low_stock': low_stock,
    }
    return render(request, 'pharmacy/pharmacist_dashboard.html', context)

class PharmacistRequiredMixin:
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_pharmacist(request.user):
            messages.error(request, "Access denied. You are not a pharmacist.")
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)

class MedicineListView(PharmacistRequiredMixin, ListView):
    model = Medicine
    template_name = 'pharmacy/medicine_list.html'
    context_object_name = 'medicines'

class MedicineCreateView(PharmacistRequiredMixin, CreateView):
    model = Medicine
    template_name = 'pharmacy/medicine_form.html'
    fields = ['name', 'formula', 'usage_instructions', 'manufacturer', 'price', 'stock_quantity', 'expiry_date', 'requires_prescription', 'image']
    success_url = reverse_lazy('pharmacy:medicine_list')

class MedicineUpdateView(PharmacistRequiredMixin, UpdateView):
    model = Medicine
    template_name = 'pharmacy/medicine_form.html'
    fields = ['name', 'formula', 'usage_instructions', 'manufacturer', 'price', 'stock_quantity', 'expiry_date', 'requires_prescription', 'image']
    success_url = reverse_lazy('pharmacy:medicine_list')

class MedicineDeleteView(PharmacistRequiredMixin, DeleteView):
    model = Medicine
    template_name = 'pharmacy/medicine_confirm_delete.html'
    success_url = reverse_lazy('pharmacy:medicine_list')

@login_required
def update_stock(request, pk):
    if request.method == 'POST':
        if not is_pharmacist(request.user):
            messages.error(request, "Access denied.")
            return redirect('core:home')
            
        medicine = get_object_or_404(Medicine, pk=pk)
        action = request.POST.get('action') 
        amount = int(request.POST.get('amount', 0))
        
        if amount > 0:
            if action == 'add':
                medicine.stock_quantity += amount
                messages.success(request, f"Added {amount} stock to {medicine.name}.")
            elif action == 'remove':
                if medicine.stock_quantity >= amount:
                    medicine.stock_quantity -= amount
                    messages.success(request, f"Removed {amount} stock from {medicine.name}.")
                else:
                    messages.error(request, "Cannot remove more stock than available!")
            
            medicine.save()
            
    return redirect('pharmacy:medicine_list')

@login_required
def billing_pos(request):
    if not is_pharmacist(request.user):
        messages.error(request, "Access denied.")
        return redirect('core:home')
    
    medicines = Medicine.objects.filter(stock_quantity__gt=0)
    
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name')
        medicine_ids = request.POST.getlist('medicine_id[]')
        quantities = request.POST.getlist('quantity[]')
        
        if not medicine_ids:
            messages.error(request, "Please select at least one medicine.")
            return redirect('pharmacy:billing_pos')
            
        bill = PharmacyBill.objects.create(
            patient_name=patient_name,
            pharmacist=request.user.pharmacist_profile if hasattr(request.user, 'pharmacist_profile') else None,
            total_amount=0
        )
        
        total = 0
        for med_id, qty in zip(medicine_ids, quantities):
            try:
                med = Medicine.objects.get(id=med_id)
                q = int(qty)
                if q > med.stock_quantity:
                    messages.error(request, f"Not enough stock for {med.name}!")
                    bill.delete()
                    return redirect('pharmacy:billing_pos')
                
                cost = med.price * q
                total += cost
                PharmacyBillItem.objects.create(bill=bill, medicine=med, quantity=q, price=med.price)
                med.stock_quantity -= q
                med.save()
            except BaseException as e:
                pass
                
        bill.total_amount = total
        bill.save()
        messages.success(request, f"Bill created successfully! Total: ${total}")
        return redirect('pharmacy:pharmacist_dashboard')
        
    return render(request, 'pharmacy/billing_pos.html', {'medicines': medicines})

def public_pharmacy_list(request):
    query = request.GET.get('q', '')
    if query:
        medicines = Medicine.objects.filter(name__icontains=query)
    else:
        medicines = Medicine.objects.all()
    return render(request, 'pharmacy/public_list.html', {'medicines': medicines, 'query': query})

from .models import PatientCart, PatientCartItem, UnifiedBill
from appointments.models import Appointment

@login_required
def add_to_cart(request, medicine_id):
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, "Only patients can add medicines to the cart.")
        return redirect('pharmacy:public_list')
        
    medicine = get_object_or_404(Medicine, id=medicine_id)
    if medicine.stock_quantity <= 0:
        messages.error(request, f"{medicine.name} is out of stock.")
        return redirect('pharmacy:public_list')
        
    quantity = 1
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1
            
    cart, created = PatientCart.objects.get_or_create(patient=request.user.patient_profile)
    cart_item, item_created = PatientCartItem.objects.get_or_create(cart=cart, medicine=medicine)
    
    if not item_created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity <= medicine.stock_quantity:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"Added {quantity} more {medicine.name} to your cart.")
        else:
            messages.error(request, f"Cannot add more of {medicine.name}. Max stock reached.")
    else:
        if quantity <= medicine.stock_quantity:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f"Added {quantity}x {medicine.name} to your cart.")
        else:
            messages.error(request, f"Cannot add {quantity}. Only {medicine.stock_quantity} available.")
            cart_item.delete()
        
    return redirect('pharmacy:public_list')

@login_required
def remove_from_cart(request, item_id):
    if not hasattr(request.user, 'patient_profile'):
        return redirect('core:home')
        
    cart_item = get_object_or_404(PatientCartItem, id=item_id, cart__patient=request.user.patient_profile)
    cart_item.delete()
    messages.success(request, f"Removed {cart_item.medicine.name} from your cart.")
    return redirect('pharmacy:view_cart')

@login_required
def view_cart(request):
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, "Only patients have carts.")
        return redirect('core:home')
        
    cart, created = PatientCart.objects.get_or_create(patient=request.user.patient_profile)
    cart_items = cart.items.all()
    
    total_medicine_cost = sum(item.quantity * item.medicine.price for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_medicine_cost': total_medicine_cost,
    }
    return render(request, 'pharmacy/cart.html', context)

@login_required
def unified_checkout(request):
    if not hasattr(request.user, 'patient_profile'):
        return redirect('core:home')
        
    patient = request.user.patient_profile
    cart, created = PatientCart.objects.get_or_create(patient=patient)
    cart_items = cart.items.all()
    
    # Calculate medicine cost
    total_medicine_cost = sum(item.quantity * item.medicine.price for item in cart_items)
    
    # Calculate unpaid appointments
    unpaid_appointments = Appointment.objects.filter(patient=patient, is_paid=False, status__in=['Pending', 'Confirmed', 'Completed'])
    total_consultation_cost = sum(appt.doctor.consultation_fee for appt in unpaid_appointments)
    
    grand_total = total_medicine_cost + total_consultation_cost
    
    if request.method == 'POST':
        # Verify stock again
        for item in cart_items:
            if item.quantity > item.medicine.stock_quantity:
                messages.error(request, f"Not enough stock for {item.medicine.name}. Please remove or reduce quantity.")
                return redirect('pharmacy:view_cart')
                
        # Generate Unified Bill
        bill = UnifiedBill.objects.create(
            patient=patient,
            total_medicine_cost=total_medicine_cost,
            total_consultation_cost=total_consultation_cost,
            grand_total=grand_total,
            is_paid=True
        )
        
        # Deduct stock
        for item in cart_items:
            med = item.medicine
            med.stock_quantity -= item.quantity
            med.save()
            
        # Empty cart
        cart_items.delete()
        
        # Mark appointments as paid
        for appt in unpaid_appointments:
            appt.is_paid = True
            appt.save()
            
        messages.success(request, f"Successfully processed payment of ${grand_total}. Bill #{bill.id} generated.")
        return redirect('core:home')
        
    context = {
        'cart_items': cart_items,
        'unpaid_appointments': unpaid_appointments,
        'total_medicine_cost': total_medicine_cost,
        'total_consultation_cost': total_consultation_cost,
        'grand_total': grand_total,
    }
    return render(request, 'pharmacy/checkout.html', context)

@login_required
def expenditure_history(request):
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, "Only patients have a billing history.")
        return redirect('core:home')
        
    bills = UnifiedBill.objects.filter(patient=request.user.patient_profile).order_by('-date')
    return render(request, 'pharmacy/expenditure_history.html', {'bills': bills})

@login_required
def unified_bill_detail(request, bill_id):
    bill = get_object_or_404(UnifiedBill, id=bill_id)
    
    # Ensure only the patient or a staff member can view it
    if not (request.user.is_pharmacist or request.user.is_doctor or request.user.is_receptionist or (hasattr(request.user, 'patient_profile') and bill.patient == request.user.patient_profile)):
        messages.error(request, "Access denied.")
        return redirect('core:home')
        
    return render(request, 'pharmacy/unified_bill_detail.html', {'bill': bill})

@login_required
def pay_unified_bill(request, bill_id):
    bill = get_object_or_404(UnifiedBill, id=bill_id)
    
    if not hasattr(request.user, 'patient_profile') or bill.patient != request.user.patient_profile:
        messages.error(request, "Access denied.")
        return redirect('core:home')
        
    if request.method == 'POST':
        # Simulate payment processing
        bill.is_paid = True
        bill.save()
        
        if bill.appointment:
            bill.appointment.is_paid = True
            bill.appointment.save()
            
            # Deduct stock for prescribed medicines
            for prescribed in bill.appointment.prescribed_medicines.all():
                if prescribed.medicine.stock_quantity >= prescribed.quantity:
                    prescribed.medicine.stock_quantity -= prescribed.quantity
                    prescribed.medicine.save()
                else:
                    messages.warning(request, f"Low stock warning for {prescribed.medicine.name}.")
                    
        messages.success(request, f"Successfully paid Unified Bill #{bill.id}")
        return redirect('pharmacy:expenditure_history')
        
    return redirect('pharmacy:unified_bill_detail', bill_id=bill.id)
