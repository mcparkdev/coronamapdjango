from django import forms
from .models import Case

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case        
        skip_unchanged = True
        report_skipped = False
        fields = ('caseID', 'date', 'city', 'locality', 'age', 'sex', 'type', 'place',' state')