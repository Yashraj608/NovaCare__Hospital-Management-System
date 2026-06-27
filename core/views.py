from django.shortcuts import render, redirect
from accounts.models import Doctor, Department
from .models import Service

def home(request):
    departments = Department.objects.all()[:4] # Get top 4 for homepage
    return render(request, 'core/home.html', {'departments': departments})

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

def branches(request):
    return render(request, 'core/branches.html')

def services(request):
    all_services = Service.objects.filter(is_available=True)
    return render(request, 'core/services.html', {'services': all_services})

from django.db.models import Q

def doctors(request):
    search_query = request.GET.get('search', '')
    department_query = request.GET.get('department', '')
    
    docs = Doctor.objects.all()
    
    if search_query:
        docs = docs.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
        
    if department_query:
        docs = docs.filter(department__name__icontains=department_query)
    
    # Add this debug line
    print(f"Rendering doctors template with {docs.count()} doctors")
    for doc in docs:
        print(f"  Doctor: {doc.user.username}, Name: {doc.user.get_full_name()}")
    
    return render(request, 'core/doctors.html', {
        'doctors': docs,
        'departments': Department.objects.all(),
        'active_department': department_query 
    })

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from accounts.models import User, Department

@login_required
def add_doctor(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        fn = request.POST.get('first_name')
        ln = request.POST.get('last_name')
        
        dept_id = request.POST.get('department')
        exp = request.POST.get('experience', 0)
        fee = request.POST.get('fee', 0.0)
        avail = request.POST.get('availability', '')
        prof_pic = request.FILES.get('profile_picture')
        
        if User.objects.filter(username=u).exists():
            return render(request, 'core/add_doctor.html', {
                'error': 'Username already exists.',
                'departments': Department.objects.all()
            })
            
        try:
            # Create User
            user = User.objects.create_user(
                username=u, 
                email=e, 
                password=p, 
                first_name=fn, 
                last_name=ln, 
                is_doctor=True
            )
            
            # Create Doctor Profile
            dept = Department.objects.get(id=dept_id) if dept_id else None
            Doctor.objects.create(
                user=user,
                department=dept,
                experience_years=exp,
                consultation_fee=fee,
                availability=avail,
                profile_picture=prof_pic
            )
            messages.success(request, f"Successfully added Dr. {fn} {ln} to the directory.")
            return redirect('accounts:admin_doctors')
        except Exception as ex:
            return render(request, 'core/add_doctor.html', {
                'error': f'An error occurred: {str(ex)}',
                'departments': Department.objects.all()
            })
            
    return render(request, 'core/add_doctor.html', {'departments': Department.objects.all()})

@login_required
def delete_doctor(request, doctor_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
    if request.method == 'POST':
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            user_account = doctor.user
            doctor_name = user_account.get_full_name() or user_account.username
            user_account.delete()  # This cascades and deletes the Doctor profile too
            messages.success(request, f"Successfully deleted Dr. {doctor_name}.")
        except Doctor.DoesNotExist:
            messages.error(request, "Doctor not found.")
        except Exception as e:
            messages.error(request, f"Error deleting doctor: {e}")
    
    return redirect('accounts:admin_doctors')

from django.shortcuts import get_object_or_404

@login_required
def edit_doctor(request, doctor_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('core:home')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    user_acc = doctor.user
    departments = Department.objects.all()
    
    if request.method == 'POST':
        fn = request.POST.get('first_name')
        ln = request.POST.get('last_name')
        e = request.POST.get('email')
        
        dept_id = request.POST.get('department')
        exp = request.POST.get('experience', 0)
        fee = request.POST.get('fee', 0.0)
        avail = request.POST.get('availability', '')
        prof_pic = request.FILES.get('profile_picture')
        
        try:
            user_acc.first_name = fn
            user_acc.last_name = ln
            user_acc.email = e
            user_acc.save()
            
            dept = Department.objects.get(id=dept_id) if dept_id else None
            doctor.department = dept
            doctor.experience_years = exp
            doctor.consultation_fee = fee
            doctor.availability = avail
            if prof_pic:
                doctor.profile_picture = prof_pic
            doctor.save()
            
            messages.success(request, f"Successfully updated Dr. {fn} {ln}.")
            return redirect('accounts:admin_doctors')
        except Exception as ex:
            return render(request, 'core/edit_doctor.html', {
                'error': f'An error occurred: {str(ex)}',
                'doctor': doctor,
                'departments': departments
            })
            
    return render(request, 'core/edit_doctor.html', {
        'doctor': doctor, 
        'departments': departments
    })