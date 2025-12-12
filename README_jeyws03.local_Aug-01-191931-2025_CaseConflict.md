# IPScanner

A Django application to scan IP networks provided via a web form and export the results as a CSV file compatible with NetBox.

---

## Features

- Scan multiple IP networks submitted via a web form
- Export scan results (IP and hostname) as a CSV file
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
    networks = forms.CharField(widget=forms.Textarea, help_text="Enter a list of IP networks (one per line).")
```

---

## Views

In `scanner/views.py`:

```python
import csv
import socket
from django.http import HttpResponse
from django.shortcuts import render
from .forms import IPNetworkForm
import ipaddress

def scan_ip(ip):
    try:
        socket.setdefaulttimeout(1)
        result = socket.gethostbyaddr(ip)
        return result[0]
    except socket.herror:
        return "Unresolved"

def scan_networks(networks):
    results = []
    for network in networks:
        try:
            ip_net = ipaddress.ip_network(network.strip())
            for ip in ip_net.hosts():
                hostname = scan_ip(str(ip))
                results.append({'ip': str(ip), 'hostname': hostname})
        except ValueError:
            results.append({'error': f'Invalid network: {network}'})
    return results

def ip_scan_view(request):
    if request.method == 'POST':
        form = IPNetworkForm(request.POST)
        if form.is_valid():
            networks = form.cleaned_data['networks'].splitlines()
            scan_results = scan_networks(networks)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="scan_results.csv"'
            writer = csv.DictWriter(response, fieldnames=['ip', 'hostname'])
            writer.writeheader()
            for row in scan_results:
                writer.writerow(row)
            return response
    else:
        form = IPNetworkForm()
    return render(request, 'scanner/ip_scan.html', {'form': form})
```

---

## Templates

Create `scanner/templates/scanner/ip_scan.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>IP Network Scanner</title>
</head>
<body>
    <h1>Scan IP Networks</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Start Scan</button>
    </form>
</body>
</html>
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

3. Open [http://127.0.0.1:8000/scan/](http://127.0.0.1:8000/scan/) in your browser to use the scanner form.

---

## Export & NetBox

The generated CSV will have `ip` and `hostname` columns, compatible with NetBox import. Adjust as needed for your NetBox setup.

---

## Contributing

Feel free to open issues or submit pull requests!

---

## License

MIT
