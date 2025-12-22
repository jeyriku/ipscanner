from django import forms
from django.core.exceptions import ValidationError
import ipaddress


class IPNetworkForm(forms.Form):
    networks = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}),
        help_text="Saisissez une liste de réseaux IP (un par ligne) ou sélectionnez un réseau local ci-dessous.",
        label="Réseaux IP"
    )

    local_network = forms.ChoiceField(
        choices=[],
        required=False,
        label="Réseaux détectés sur vos interfaces",
        help_text="Sélectionnez un réseau détecté pour l'ajouter à la liste ci-dessus."
    )

    def __init__(self, *args, **kwargs):
        local_network_choices = kwargs.pop('local_network_choices', None)
        super().__init__(*args, **kwargs)
        if local_network_choices:
            self.fields['local_network'].choices = [(n, n) for n in local_network_choices]
        else:
            self.fields['local_network'].choices = []

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
