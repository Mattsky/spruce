from django import forms
from django.core import validators

class ScanForm(forms.Form):

	scan_address = forms.CharField(validators=['validators.validate_ipv46_address'])
	
	#raise forms.ValidationError("INVALID")

	#def clean_address(self):
		#data = self.cleaned_data['scan_address']
