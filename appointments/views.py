from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment, PrescribedMedicine
from accounts.models import Doctor
from pharmacy.models import Medicine, UnifiedBill
from datetime import datetime

@login_required
def book_appointment(request):
    if hasattr(request.user, 'doctor_profile'):
        messages.error(request, "Doctors cannot book appointments as patients. Please login with a patient account.")
        return redirect('core:home')
        
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, "Only registered patients can book appointments.")
        return redirect('core:home')
        
    doctors = Doctor.objects.all()
    selected_doc_id = request.GET.get('doc', None)
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        symptoms = request.POST.get('symptoms')
        
        doctor = get_object_or_404(Doctor, id=doctor_id)
        
        # Check if slot is taken
        if Appointment.objects.filter(doctor=doctor, date=date_str, time=time_str).exists():
            messages.error(request, f"Dr. {doctor.user.get_full_name() or doctor.user.username} is already booked at that time. Please select another slot.")
            return render(request, 'appointments/book.html', {'doctors': doctors, 'selected_doc': doctor_id})
            
        Appointment.objects.create(
            patient=request.user.patient_profile,
            doctor=doctor,
            date=date_str,
            time=time_str,
            symptoms=symptoms
        )
        
        messages.success(request, f"Appointment successfully booked with Dr. {doctor.user.get_full_name() or doctor.user.username} on {date_str} at {time_str}.")
        return redirect('accounts:patient_dashboard')
        
    return render(request, 'appointments/book.html', {'doctors': doctors, 'selected_doc': selected_doc_id})

@login_required
def approve_appointment(request, appointment_id):
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('core:home')
        
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor_profile)
    appointment.status = 'Confirmed'
    appointment.save()
    messages.success(request, f"Appointment for {appointment.patient.user.get_full_name() or appointment.patient.user.username} confirmed.")
    return redirect('accounts:doctor_dashboard')

@login_required
def cancel_appointment(request, appointment_id):
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('core:home')
        
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor_profile)
    appointment.status = 'Cancelled'
    appointment.save()
    messages.info(request, f"Appointment for {appointment.patient.user.get_full_name() or appointment.patient.user.username} cancelled.")
    return redirect('accounts:doctor_dashboard')

@login_required
def add_consultation_notes(request, appointment_id):
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('core:home')
        
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor_profile)
    medicines = Medicine.objects.all()
    
    if request.method == 'POST':
        diagnosis = request.POST.get('disease_diagnosis', '')
        prescription_notes = request.POST.get('prescription', '')
        tests = request.POST.get('test_reports', '')
        
        appointment.disease_diagnosis = diagnosis
        appointment.prescription = prescription_notes
        appointment.test_reports = tests
        appointment.status = 'Completed'
        appointment.save()
        
        # Handle dynamic prescribed medicines
        medicine_ids = request.POST.getlist('medicine[]')
        quantities = request.POST.getlist('quantity[]')
        dosages = request.POST.getlist('dosage[]')
        
        total_medicine_cost = 0
        
        for i in range(len(medicine_ids)):
            med_id = medicine_ids[i]
            if med_id:
                med = get_object_or_404(Medicine, id=med_id)
                qty = int(quantities[i]) if i < len(quantities) and quantities[i].isdigit() else 1
                dos = dosages[i] if i < len(dosages) else ''
                
                PrescribedMedicine.objects.create(
                    appointment=appointment,
                    medicine=med,
                    quantity=qty,
                    dosage_instructions=dos
                )
                total_medicine_cost += (med.price * qty)
                
        # Generate Unified Bill
        consultation_cost = appointment.doctor.consultation_fee
        grand_total = float(consultation_cost) + float(total_medicine_cost)
        
        UnifiedBill.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            total_medicine_cost=total_medicine_cost,
            total_consultation_cost=consultation_cost,
            grand_total=grand_total
        )
        
        messages.success(request, f"Consultation notes added for {appointment.patient.user.get_full_name() or appointment.patient.user.username}. Unified Bill generated.")
        return redirect('accounts:doctor_dashboard')
        
    return render(request, 'appointments/appointment_notes_form.html', {'appointment': appointment, 'medicines': medicines})

@login_required
def patient_medical_history(request, patient_id):
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, "Only doctors can view patient medical histories.")
        return redirect('core:home')
        
    from accounts.models import Patient
    patient = get_object_or_404(Patient, id=patient_id)
    
    history = Appointment.objects.filter(patient=patient, status='Completed').order_by('-date', '-time')
    
    context = {
        'patient': patient,
        'history': history,
    }
    return render(request, 'appointments/patient_medical_history.html', context)

@login_required
def appointment_detail(request, appointment_id):
    # This view is for patients to view their own completed appointment
    # Doctors can also use it if needed, but they have patient_medical_history
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions (only the patient or the assigned doctor)
    is_patient = hasattr(request.user, 'patient_profile') and appointment.patient == request.user.patient_profile
    is_doctor = hasattr(request.user, 'doctor_profile') and appointment.doctor == request.user.doctor_profile
    
    if not (is_patient or is_doctor):
        messages.error(request, "Access denied.")
        return redirect('core:home')
        
    try:
        bill = appointment.unifiedbill
    except UnifiedBill.DoesNotExist:
        bill = None
        
    context = {
        'appointment': appointment,
        'medicines': appointment.prescribed_medicines.all(),
        'bill': bill
    }
    
    return render(request, 'appointments/appointment_detail.html', context)
