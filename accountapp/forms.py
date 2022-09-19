from allauth.account import forms
from allauth.account.forms import SignupForm


# class CustomSignupForm(SignupForm):
#     name = forms.CharField(label='이름')
#
#     def save(self, request):
#         user = super(CustomSignupForm, self).save(request)
#         user.name = self.cleaned_data['name']
#         user.save()
#         return user
