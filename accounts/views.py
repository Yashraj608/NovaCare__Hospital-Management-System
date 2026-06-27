from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import User, Patient, Doctor
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('accounts:admin_dashboard')
        elif getattr(request.user, 'is_doctor', False):
            return redirect('accounts:doctor_dashboard')
        else:
            return redirect('accounts:patient_dashboard')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            if user.is_superuser or user.is_staff:
                return redirect('accounts:admin_dashboard')
            elif getattr(user, 'is_doctor', False):
                return redirect('accounts:doctor_dashboard')
            return redirect('accounts:patient_dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials. Please try again.'})
            
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        fn = request.POST.get('first_name')
        ln = request.POST.get('last_name')
        
        if User.objects.filter(username=u).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already exists.'})
            
        user = User.objects.create_user(username=u, email=e, password=p, first_name=fn, last_name=ln, is_patient=True)
        
        # Create corresponding Patient profile
        Patient.objects.create(user=user)
        
        login(request, user)
        messages.success(request, "Registration successful! Welcome to NovaCare.")
        return redirect('accounts:patient_dashboard')
        
    return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:home')

@login_required
def patient_dashboard(request):
    if not getattr(request.user, 'is_patient', False) and not request.user.is_superuser:
        return redirect('core:home')
    
    try:
        patient = request.user.patient_profile
        appointments = patient.appointments.all().order_by('-date', '-time')
    except:
        appointments = []
        
    return render(request, 'accounts/patient_dashboard.html', {'appointments': appointments})

@login_required
def doctor_dashboard(request):
    if not getattr(request.user, 'is_doctor', False):
        return redirect('core:home')
        
    try:
        doctor = request.user.doctor_profile
        all_appointments = doctor.appointments.all().order_by('date', 'time')
        pending = all_appointments.filter(status='Pending')
        confirmed = all_appointments.filter(status='Confirmed')
        completed = all_appointments.filter(status='Completed')
        cancelled = all_appointments.filter(status='Cancelled')
    except:
        all_appointments = pending = confirmed = completed = cancelled = []
        
    context = {
        'appointments': all_appointments,
        'pending': pending,
        'confirmed': confirmed,
        'completed': completed,
        'cancelled': cancelled,
        'pending_count': pending.count() if hasattr(pending, 'count') else 0,
        'confirmed_count': confirmed.count() if hasattr(confirmed, 'count') else 0,
        'completed_count': completed.count() if hasattr(completed, 'count') else 0,
    }
    return render(request, 'accounts/doctor_dashboard.html', context)


@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    from appointments.models import Appointment
    from pharmacy.models import Medicine, UnifiedBill
    from accounts.models import Department
    from django.db.models import Sum
    from datetime import date
    
    today = date.today()
    
    # Overview Stats
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    
    # Calculate Total Revenue
    total_revenue = UnifiedBill.objects.filter(is_paid=True).aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    
    # Calculate Monthly Revenue for Chart
    monthly_revenue = []
    for month in range(1, 13):
        # Query unified bills for this month
        month_bills = UnifiedBill.objects.filter(
            is_paid=True, 
            date__year=today.year, 
            date__month=month
        ).aggregate(Sum('grand_total'))['grand_total__sum'] or 0
        monthly_revenue.append(float(month_bills))
    
    # Reports/Alerts (Low stock medicines)
    low_stock_medicines = Medicine.objects.filter(stock_quantity__lt=20).order_by('stock_quantity')[:5]
    
    # Recent Appointments (Table)
    recent_appointments = Appointment.objects.all().order_by('-date', '-time')[:5]
    
    # Agenda (Today's Appointments)
    todays_agenda = Appointment.objects.filter(date=today).order_by('time')[:5]
    
    # Doctors Schedule (just a list of doctors for now)
    doctors = Doctor.objects.all()
    
    # Chart Data: Patients by Department
    departments = Department.objects.all()
    dept_labels = []
    dept_data = []
    for dept in departments:
        count = Appointment.objects.filter(doctor__department=dept).count()
        if count > 0:
            dept_labels.append(dept.name)
            dept_data.append(count)
            
    context = {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_revenue': float(total_revenue),
        'monthly_revenue': monthly_revenue,
        'low_stock_medicines': low_stock_medicines,
        'recent_appointments': recent_appointments,
        'todays_agenda': todays_agenda,
        'doctors': doctors,
        'dept_labels': dept_labels,
        'dept_data': dept_data,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def admin_appointments(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    from appointments.models import Appointment
    from datetime import date, timedelta
    
    today = date.today()
    
    # All appointments for the table
    all_appointments = Appointment.objects.all().order_by('-date', '-time')
    
    # Stats
    todays_appointments = all_appointments.filter(date=today)
    todays_count = todays_appointments.count()
    completed_count = all_appointments.filter(status='Completed').count()
    ongoing_count = all_appointments.filter(status__in=['Pending', 'Confirmed']).count()
    canceled_count = all_appointments.filter(status='Cancelled').count()
    
    # Trend Chart Data (Last 7 Days)
    days_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        days_labels.append(target_date.strftime("%a")) # Mon, Tue, etc
        count = all_appointments.filter(date=target_date).count()
        trend_data.append(count)
        
    # Appointment Type Data (Mocking types since DB only tracks status)
    type_data = [
        all_appointments.filter(status='Completed').count(), # Consultation
        all_appointments.filter(status='Confirmed').count(), # Follow-up
        all_appointments.filter(status='Pending').count(), # Surgery/Other
        all_appointments.filter(status='Cancelled').count() # Telemedicine
    ]
        
    context = {
        'all_appointments': all_appointments,
        'todays_count': todays_count,
        'completed_count': completed_count,
        'ongoing_count': ongoing_count,
        'canceled_count': canceled_count,
        'days_labels': days_labels,
        'trend_data': trend_data,
        'type_data': type_data,
    }
    
    return render(request, 'accounts/admin_appointments.html', context)

@login_required
def admin_update_appointment_status(request, appt_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    if request.method == 'POST':
        from appointments.models import Appointment
        appt = get_object_or_404(Appointment, id=appt_id)
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            appt.status = new_status
            appt.save()
            messages.success(request, f"Appointment status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status selected.")
            
    return redirect('accounts:admin_appointments')

@login_required
def admin_doctors(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    from accounts.models import Department, Doctor
    
    doctors = Doctor.objects.all().order_by('user__first_name')
    departments = Department.objects.all().order_by('name')
    
    context = {
        'doctors': doctors,
        'departments': departments,
    }
    return render(request, 'accounts/admin_doctors.html', context)

@login_required
def admin_patients(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    patients = Patient.objects.all().order_by('-user__date_joined')
    return render(request, 'accounts/admin_patients.html', {'patients': patients})

@login_required
def admin_view_patient(request, patient_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
    patient = get_object_or_404(Patient, id=patient_id)
    appointments = patient.appointments.all().order_by('-date', '-time')
    return render(request, 'accounts/admin_patient_detail.html', {'patient': patient, 'appointments': appointments})

@login_required
def admin_delete_patient(request, patient_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
    if request.method == 'POST':
        patient = get_object_or_404(Patient, id=patient_id)
        user_account = patient.user
        patient_name = user_account.get_full_name() or user_account.username
        user_account.delete()
        messages.success(request, f"Successfully deleted Patient '{patient_name}'.")
    return redirect('accounts:admin_patients')

@login_required
def admin_departments(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    from accounts.models import Department
    departments = Department.objects.all().order_by('name')
    return render(request, 'accounts/admin_departments.html', {'departments': departments})

@login_required
def admin_add_department(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    from accounts.models import Department
    
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('description', '')
        icon = request.FILES.get('icon')
        
        try:
            Department.objects.create(name=name, description=desc, icon=icon)
            messages.success(request, f"Successfully added department '{name}'.")
            return redirect('accounts:admin_departments')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    return render(request, 'accounts/admin_department_form.html', {'action': 'Add'})

@login_required
def admin_edit_department(request, dept_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    from accounts.models import Department
    department = get_object_or_404(Department, id=dept_id)
    
    if request.method == 'POST':
        department.name = request.POST.get('name')
        department.description = request.POST.get('description', '')
        icon = request.FILES.get('icon')
        if icon:
            department.icon = icon
            
        try:
            department.save()
            messages.success(request, f"Successfully updated department '{department.name}'.")
            return redirect('accounts:admin_departments')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    return render(request, 'accounts/admin_department_form.html', {'action': 'Edit', 'department': department})

from django.shortcuts import get_object_or_404

@login_required
def admin_delete_doctor(request, doctor_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
    if request.method == 'POST':
        from accounts.models import Doctor
        doctor = get_object_or_404(Doctor, id=doctor_id)
        user_account = doctor.user
        doctor_name = user_account.get_full_name() or user_account.username
        user_account.delete()
        messages.success(request, f"Successfully deleted Dr. {doctor_name}.")
    return redirect('accounts:admin_doctors')

@login_required
def admin_delete_department(request, dept_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
    if request.method == 'POST':
        from accounts.models import Department
        department = get_object_or_404(Department, id=dept_id)
        dept_name = department.name
        department.delete()
        messages.success(request, f"Successfully deleted department '{dept_name}'.")
    return redirect('accounts:admin_departments')

@login_required
def admin_services(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    from core.models import Service
    services = Service.objects.all().order_by('name')
    return render(request, 'accounts/admin_services.html', {'services': services})

@login_required
def admin_add_service(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    from core.models import Service
    
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('description', '')
        price = request.POST.get('price', 0.00)
        is_available = request.POST.get('is_available') == 'on'
        image = request.FILES.get('image')
        
        try:
            Service.objects.create(
                name=name, 
                description=desc, 
                price=price,
                is_available=is_available,
                image=image
            )
            messages.success(request, f"Successfully added service '{name}'.")
            return redirect('accounts:admin_services')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    return render(request, 'accounts/admin_service_form.html', {'action': 'Add'})

@login_required
def admin_edit_service(request, service_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    from core.models import Service
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.description = request.POST.get('description', '')
        service.price = request.POST.get('price', 0.00)
        service.is_available = request.POST.get('is_available') == 'on'
        
        image = request.FILES.get('image')
        if image:
            service.image = image
            
        try:
            service.save()
            messages.success(request, f"Successfully updated service '{service.name}'.")
            return redirect('accounts:admin_services')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    return render(request, 'accounts/admin_service_form.html', {'action': 'Edit', 'service': service})

@login_required
def admin_delete_service(request, service_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
        
    from core.models import Service
    if request.method == 'POST':
        service = get_object_or_404(Service, id=service_id)
        service_name = service.name
        service.delete()
        messages.success(request, f"Successfully deleted service '{service_name}'.")
    return redirect('accounts:admin_services')

