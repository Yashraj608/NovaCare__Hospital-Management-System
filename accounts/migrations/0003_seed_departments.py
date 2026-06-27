from django.db import migrations

DEPARTMENTS = [
    ("General Medicine", "Diagnosis and treatment of adult diseases and general health conditions."),
    ("Emergency Medicine", "Immediate care for acute illnesses, injuries, and life-threatening conditions."),
    ("Internal Medicine", "Comprehensive care for complex diseases in adult patients."),
    ("Cardiology", "Diagnosis and treatment of heart and cardiovascular system disorders."),
    ("Neurology", "Disorders of the brain, spinal cord, and nervous system."),
    ("Orthopedics", "Conditions of the musculoskeletal system, including bones, joints, and muscles."),
    ("Pediatrics", "Medical care for infants, children, and adolescents."),
    ("Gynecology & Obstetrics", "Women's reproductive health, pregnancy, and childbirth."),
    ("Oncology", "Diagnosis and treatment of cancer."),
    ("Dermatology", "Skin, hair, and nail disorders."),
    ("Ophthalmology", "Eye and vision disorders and surgery."),
    ("ENT (Ear, Nose & Throat)", "Disorders of the ear, nose, throat, and related structures."),
    ("Psychiatry", "Mental health disorders including depression, anxiety, and schizophrenia."),
    ("Pulmonology", "Lung and respiratory tract diseases."),
    ("Gastroenterology", "Digestive system disorders including stomach, liver, and intestines."),
    ("Nephrology", "Kidney diseases and renal function disorders."),
    ("Urology", "Urinary tract conditions and male reproductive health."),
    ("Endocrinology", "Hormonal disorders including diabetes and thyroid conditions."),
    ("Rheumatology", "Autoimmune and musculoskeletal diseases like arthritis and lupus."),
    ("Hematology", "Blood and bone marrow disorders including anemia and leukemia."),
    ("Infectious Diseases", "Diseases caused by bacteria, viruses, fungi, and parasites."),
    ("Immunology & Allergy", "Immune system disorders, allergies, and hypersensitivity reactions."),
    ("Anesthesiology", "Anesthesia management during surgeries and procedures."),
    ("Radiology", "Medical imaging including X-rays, MRI, CT scans, and ultrasound."),
    ("Pathology", "Diagnosis of disease through examination of tissue, cells, and body fluids."),
    ("General Surgery", "Surgical procedures involving the abdomen, skin, and soft tissues."),
    ("Neurosurgery", "Surgical treatment of brain, spine, and nervous system conditions."),
    ("Cardiothoracic Surgery", "Surgery on the heart, lungs, and chest cavity."),
    ("Plastic & Reconstructive Surgery", "Cosmetic and reconstructive procedures for skin and soft tissue."),
    ("Vascular Surgery", "Surgery on blood vessels excluding the heart and brain."),
    ("Transplant Surgery", "Organ transplantation including kidney, liver, and heart."),
    ("Neonatology", "Medical care for newborns, especially premature and critically ill infants."),
    ("Geriatrics", "Health care for elderly patients and age-related conditions."),
    ("Palliative Care", "Comfort care for patients with serious, chronic, or terminal illness."),
    ("Sports Medicine", "Prevention and treatment of sports-related injuries and exercise conditions."),
    ("Rehabilitation Medicine", "Physical restoration of patients after illness, surgery, or injury."),
    ("Pain Management", "Diagnosis and treatment of chronic and acute pain conditions."),
    ("Nuclear Medicine", "Use of radioactive substances for diagnosis and therapy."),
    ("Dentistry & Oral Surgery", "Oral health, dental surgery, and disorders of the mouth and jaw."),
    ("Family Medicine", "Comprehensive care for patients of all ages across a wide range of conditions."),
]


def add_departments(apps, schema_editor):
    Department = apps.get_model('accounts', 'Department')
    for name, description in DEPARTMENTS:
        Department.objects.get_or_create(name=name, defaults={'description': description})


def remove_departments(apps, schema_editor):
    Department = apps.get_model('accounts', 'Department')
    names = [d[0] for d in DEPARTMENTS]
    Department.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_is_pharmacist_pharmacist'),
    ]

    operations = [
        migrations.RunPython(add_departments, remove_departments),
    ]
