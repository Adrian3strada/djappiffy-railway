from django.utils.translation import gettext_lazy as _

EMPLOYEE_GENDER_CHOICES = [
    ('male', _('Male')),
    ('female', _('Female')),
    ('non_binary',  _('Non-binary')),
    ('other', _('Other')),
]

EMPLOYEE_BLOOD_TYPE_CHOICES = [
    ('A+', _('A+')),
    ('A-', _('A-')),
    ('B+', _('B+')),
    ('B-', _('B-')),
    ('AB+', _('AB-')),
    ('O+', _('O+')),
    ('O-', _('O-')),
    ('unknown', _('Unknown')),
]

EMPLOYEE_PAYMENT_CHOICES = [
    ('daily', _('Daily')),
    ('weekly', _('Weekly')),         
    ('fortnightly', _('Fortnightly')),  
    ('monthly', _('Monthly')),        
]

EMPLOYEE_PAYMENT_METHOD_CHOICES = [
    ('bank_transfer', _('Bank Transfer')),
    ('cash', _('Cash')),         
    ('cheque', _('Cheque')),        
]

EMPLOYEE_ACADEMIC_CHOICES = [
    ('basic_education', _('Basic Education')),
    ('upper_secondary_education', _('Upper Secondary Education')),
    ('higher_education', _('Higher Education')),
    ('none', _('None')),
]

EMERGENCY_CONTACT_RELATIONSHIP_CHOICES = [
    ('spouse', _('Spouse')),  
    ('father', _('Father')), 
    ('mother', _('Mother')), 
    ('sibling', _('Sibling')),  
    ('grandparent', _('Grandparent')),  
    ('grandchild', _('Grandchild')),  
    ('uncle_aunt', _('Uncle/Aunt')),  
    ('nephew_niece', _('Nephew/Niece')),  
    ('cousin', _('Cousin')),  
    ('friend', _('Friend')),  
    ('partner', _('Partner')),  
    ('other', _('Other')),  
]

MARITAL_STATUS_CHOICES = [
    ('single', _('Single')),  
    ('married', _('Married')), 
    ('divorced', _('Divorced')),  
    ('widowed', _('Widowed')), 
    ('separated', _('Separated')),  
    ('cohabiting', _('Cohabiting')), 
    ('other', _('Other')),  
]