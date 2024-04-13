from django import forms

class AadharImageForm(forms.Form):
    front_image = forms.ImageField(label='Front Image')
    back_image = forms.ImageField(label='Back Image')
