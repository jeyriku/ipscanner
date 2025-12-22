## Architecture requirements (Apple Silicon/Intel)

If you are on a Mac with Apple Silicon (M1/M2/M3), you must:

- Use a Python interpreter and virtual environment that matches your hardware (arm64 for Apple Silicon, x86_64 for Intel/Rosetta).
- Install all dependencies (like netifaces) in the same architecture as your Python.

**How to check your Python architecture:**

```bash
python3 -c "import platform; print(platform.machine())"
```

If you see `arm64`, you are using Apple Silicon native Python. If you see `x86_64`, you are using Intel/Rosetta Python.

**If you get errors about incompatible architecture:**

- Recreate your virtual environment with the correct Python version/architecture.
- Reinstall all dependencies:

```bash
pip uninstall netifaces
pip install --force-reinstall --no-cache-dir netifaces
```

See the troubleshooting section below for more details.
## Troubleshooting

### Django server fails to start or shows import/URL errors

If you encounter errors like:

```
Exception in thread django-main-thread:
Traceback (most recent call last):
    ...
    File "/path/to/views.py", line XX
        'ip': ip,
        ...
```

This may be due to a corrupted or badly merged `views.py` file. To fix:

1. Ensure your `views.py` matches the latest version from the repository.
2. Remove any duplicated or misplaced code blocks, especially in `nmap_scan`, `scan_networks`, and `ip_scan_view`.
3. Restart your Django server after fixing the file.

If you use Git, you can always reset to the latest working commit:

```bash
git pull origin main
```

If you need help, open an issue or contact the maintainer.
# IPScanner

A Django application to scan IP networks provided via a web form and export the results as a CSV file compatible with NetBox.

---

## Features

- Scan multiple IP networks submitted via a web form
- **Scan networks to which your local interfaces are attached (auto-detected subnets, e.g. WiFi/Ethernet)**
- Easily add detected local networks to the scan list with a dropdown in the web UI (the dropdown is always populated if your system has active interfaces with IPv4 addresses)
## Troubleshooting: Local Network Dropdown Empty

If the "Réseaux détectés sur vos interfaces" dropdown is empty:

- Make sure your computer is connected to a network (WiFi or Ethernet) and has an IPv4 address.
- The dropdown only shows IPv4 subnets (not IPv6).
- If you are running the app in a container or VM, ensure the network interfaces are visible to Python.
- You can test detection with:

    ```bash
    python3 -c "import netifaces, ipaddress; subnets = []; interfaces = netifaces.interfaces();\nfor iface in interfaces:\n    addrs = netifaces.ifaddresses(iface)\n    if netifaces.AF_INET in addrs:\n        for link in addrs[netifaces.AF_INET]:\n            ip = link.get('addr')\n            netmask = link.get('netmask')\n            if ip and netmask and not ip.startswith('127.'):\n                try:\n                    net = ipaddress.IPv4Network(f'{ip}/{netmask}', strict=False)\n                    subnets.append(str(net))\n                except Exception:\n                    continue\nprint(subnets)"
    ```
- If you see a list like `["10.188.0.0/16"]`, the backend is working. If not, check your network setup.
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
