from django import forms
from django.forms import ModelForm
from myobj.models import uClasses, objProperties
from myobj import conf as MYCONF

class actionsetparam(forms.Form):
    nameurl = forms.CharField(widget=forms.HiddenInput, max_length=255, required=False)
    idobj = forms.IntegerField(widget=forms.HiddenInput, required=False)
    idclass = forms.IntegerField(widget=forms.HiddenInput, required=False)
    params = forms.CharField(widget=forms.HiddenInput, required=False)
    objects = forms.CharField(widget=forms.HiddenInput, required=False)
    objectsno = forms.CharField(widget=forms.HiddenInput, required=False)
    exclude = forms.CharField(widget=forms.HiddenInput, max_length=1, required=False)
    order = forms.CharField(widget=forms.HiddenInput, required=False)
    order2 = forms.CharField(widget=forms.HiddenInput, required=False)
    searchcolumn = forms.CharField(widget=forms.HiddenInput, required=False)
    searchstrv = forms.CharField(widget=forms.HiddenInput, required=False)
    model = forms.CharField(widget=forms.HiddenInput, required=False)
    idobjparentobj = forms.CharField(widget=forms.HiddenInput, required=False)
    nameprop = forms.CharField(widget=forms.HiddenInput, required=False)

class FormCL(forms.Form):
    name = forms.CharField(max_length=30)
    codename = forms.SlugField(max_length=30)
    description = forms.CharField(max_length=255, widget=forms.Textarea, required=False)

class designUI(forms.Form):
    pass


class FormobjProperties(FormCL):
    myfield = forms.ChoiceField(MYCONF.TYPES_MYFIELDS_CHOICES)
    minfield = forms.CharField(max_length=4, required=False)
    maxfield = forms.CharField(max_length=4, required=False)
    required = forms.BooleanField(required=False)
    udefault = forms.CharField(max_length=255, required=False)


class FormUClasses(FormCL):
    tablespace = forms.ChoiceField(MYCONF.MYSPACE_TABLES_CHOICES)
    # if many-to-many then app '_m_NAMEmanytomanyfield'$
    properties_m_objProperties = forms.CharField(required=False, widget=forms.HiddenInput)
