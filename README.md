# IPScanner

A Django application to scan IP networks provided via a web form and export the results as a CSV file compatible with NetBox.

---

## Features

- Scan multiple IP networks submitted via a web form
- **Scan networks to which your local interfaces are attached (auto-detected subnets, e.g. WiFi/Ethernet)**
- Easily add detected local networks to the scan list with a dropdown in the web UI
- Export scan results (IP, hostname, MAC) as a CSV file
- CSV format compatible with NetBox import
- Optional: Store scan history in the database

---

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Install Django and Scapy if not already installed:

```bash
pip install django scapy
```

---

## Project Setup

Create a new Django project and app (if not already done):

```bash
django-admin startproject ipscanner
cd ipscanner
python manage.py startapp scanner
```

---

## Models

If you want to store scan history, add this to `scanner/models.py`:

```python
from django.db import models

class ScanHistory(models.Model):
    network = models.CharField(max_length=255)
    scan_date = models.DateTimeField(auto_now_add=True)
    results_file = models.FileField(upload_to='scans/')
```

---

## Forms

In `scanner/forms.py`:

```python
from django import forms

class IPNetworkForm(forms.Form):
    networks = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter a list of IP networks (one per line) or select a detected local network below."
    )
    local_network = forms.ChoiceField(
        choices=[],
        required=False,
        label="Detected local networks",
        help_text="Select a detected network to add it to the list above."
    )
```

---

## Views

In `scanner/views.py` (simplified):

```python
def get_all_local_networks():
    # Returns a list of all IPv4 subnets for all interfaces (excluding loopback)
    ...

def ip_scan_view(request):
    local_networks = get_all_local_networks()
    if request.method == "POST":
        form = IPNetworkForm(request.POST, local_network_choices=local_networks)
        if form.is_valid():
            networks = form.cleaned_data['networks'].splitlines()
            selected_local = form.cleaned_data.get('local_network')
            if selected_local and selected_local not in networks:
                networks.append(selected_local)
            # ... scan logic ...
    else:
        form = IPNetworkForm(initial={'networks': get_local_network()}, local_network_choices=local_networks)
    # ...
```

---

## Templates

The scan form now includes:

- A textarea for manual entry of networks (one per line)
- A dropdown to select from detected local networks (WiFi/Ethernet subnets)
- An "Add" button to insert the selected local network into the textarea

Example (simplified):

```html
<form method="post">
    {% csrf_token %}
    {{ form.networks.label_tag }}
    {{ form.networks }}
    {{ form.local_network.label_tag }}
    {{ form.local_network }}
    <button type="button" id="addLocalNetworkBtn">Add</button>
    <button type="submit">Start Scan</button>
</form>
<script>
    // JS to add selected local network to textarea
</script>
```

---

## URLs

In `scanner/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.ip_scan_view, name='ip_scan'),
]
```

Include this in your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('', include('scanner.urls')),
]
```

---

## Usage

1. Run migrations (if using models):

    ```bash
    python manage.py migrate
    ```

2. Start the development server:

    ```bash
    python manage.py runserver
    ```

3. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser to use the scanner form.

    - You can now select a detected local network (e.g. your WiFi subnet) from the dropdown and add it to the scan list, or enter networks manually.

---

## Export & NetBox

The generated CSV will have `ip` and `hostname` columns, compatible with NetBox import. Adjust as needed for your NetBox setup.

---

## Contributing

Feel free to open issues or submit pull requests!

---

## License

MIT
