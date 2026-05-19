from django import forms


BOOKING_TYPE_CHOICES = (
    ('hour', 'Hourly'),
    ('night', 'Nightly'),
)


class BookingRequestForm(forms.Form):
    capsule_id = forms.IntegerField(widget=forms.HiddenInput)
    booking_type = forms.ChoiceField(choices=BOOKING_TYPE_CHOICES)
    quantity = forms.IntegerField(min_value=1, max_value=30, initial=1)
    check_in_time = forms.TimeField(required=False)
    check_out_time = forms.TimeField(required=False)
    check_in_date = forms.DateField(required=False)
    check_out_date = forms.DateField(required=False)