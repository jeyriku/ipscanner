from django import forms
from django.core.exceptions import ValidationError
import ipaddress

class IPNetworkForm(forms.Form):
    networks = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}),
        help_text="Saisissez une liste de réseaux IP (un par ligne).",
        label="Réseaux IP"
    )

    def clean_networks(self):
        data = self.cleaned_data['networks']
        lines = data.strip().splitlines()

        valid_networks = []
        for line in lines:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            try:
                # Validate as IP network (CIDR format)
                network = ipaddress.ip_network(line, strict=False)
                valid_networks.append(str(network))
            except ValueError:
                raise ValidationError(f"Réseau IP invalide: {line}")

        return '\n'.join(valid_networks)
