from django.utils.translation import gettext_lazy as _

PAYMENT_CHOICES = [
        ('full', _("Full Payment")),       
        ('half', _("Half Payment")),       
        ('none', _("No Payment")),         
        ('double', _("Double Payment")),   
    ]

EMPLOYEE_GENDER_CHOICES = [
    ('male', _('Male')),
    ('female', _('Female')),
    ('non_binary',  _('Non-binary')),
    ('other', _('Other')),
    ('prefer_not_to_say', _('Prefer not to say')),
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

EMPLOYEE_STATUS_CHOICES = [
    ('active', _('Active')),
    ('inactive', _('Inactive')),
    ('vacation',  _('Vacation')),
    ('suspended', _('Suspended')),
    ('resigned', _('Resigned')),
    ('terminated', _('Terminated')),
    ('retired', _('Retired')),
    ('sick', _('Sick')),
    ('absent', _('Absent Without Reason')),
    ('special_leave', _('Special Leave')),
    ('parental_leave', _('Parental Leave')),
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
    ('check', _('Check')),        
]

EMPLOYEE_ACADEMIC_CHOICES = [
    ('basic', _('Basic')),
    ('upper_secondary', _('Upper Secondary')),
    ('higher', _('Higher')),
    ('none', _('None')),
]

EMERGENCY_CONTACT_RELATIONSHIP_CHOICES = [
    ('spouse', _('Spouse')),  
    ('father', _('Father')), 
    ('mother', _('Mother')), 
    ('child', _('Child')),  
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