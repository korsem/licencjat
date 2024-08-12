from django import forms


class HMSTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            forms.NumberInput(attrs={"class": "form-control", "placeholder": "h"}),
            forms.NumberInput(attrs={"class": "form-control", "placeholder": "m"}),
            forms.NumberInput(attrs={"class": "form-control", "placeholder": "s"}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        print("HMSTimeWidget")
        print(value)
        if value:
            h, m, s = map(int, value.split(":"))
            return [h, m, s]
        return [0, 0, 0]

    def format_output(self, rendered_widgets):
        return " ".join(rendered_widgets)


class HMSTimeField(forms.MultiValueField):
    widget = HMSTimeWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(min_value=0, required=False),
            forms.IntegerField(min_value=0, max_value=59, required=False),
            forms.IntegerField(min_value=0, max_value=59, required=False),
        )
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        print("HMSTimeField")
        print(data_list)
        if data_list:
            return f"{data_list[0]:02}:{data_list[1]:02}:{data_list[2]:02}"
        return "00:00:00"


class MSTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            forms.NumberInput(attrs={"class": "form-control", "placeholder": "m"}),
            forms.NumberInput(attrs={"class": "form-control", "placeholder": "s"}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        print("MSTimeWidget")
        print(value)
        if value:
            h, m, s = map(int, value.split(":"))
            return [h, m, s]
        return [0, 0, 0]

    def format_output(self, rendered_widgets):
        return " ".join(rendered_widgets)


class MSTimeField(forms.MultiValueField):
    widget = MSTimeWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(min_value=0, max_value=59, required=False),
            forms.IntegerField(min_value=0, max_value=59, required=False),
        )
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        print("MSTimeField")
        print(data_list)
        if data_list:
            return f"{data_list[0]:02}:{data_list[1]:02}"
        return "00:00"
