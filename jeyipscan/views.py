from django.shortcuts import render
from django.http import HttpResponse
from .forms import IPNetworkForm

import csv
import ipaddress
import socket

import nmap  # python-nmap package


def get_local_network():

    """Auto-detect the first local subnet (excluding loopback)."""
    nets = get_all_local_networks()
    if nets:
        return nets[0]
    return "127.0.0.0/24"


def get_all_local_networks():
    """Return a list of all IPv4 subnets for all interfaces (excluding loopback)."""
    subnets = []
    try:
        import netifaces
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for link in addrs[netifaces.AF_INET]:
                    ip = link.get('addr')
                    netmask = link.get('netmask')
                    if ip and netmask and not ip.startswith("127."):
                        try:
                            net = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                            subnets.append(str(net))
                        except Exception:
                            continue
    except Exception:
        pass
    return subnets


def resolve_hostname(ip):
    """Try DNS reverse lookup (PTR) for this IP."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.timeout, socket.gaierror):
        return "Non résolu"


def nmap_scan(network):
    """
    Use Nmap to scan for live hosts (-sn: no port scan) and return IP, MAC, and hostname.
    """
    scanner = nmap.PortScanner()
    results = []

    try:
        scanner.scan(hosts=network, arguments='-sn')

        for host in scanner.all_hosts():
            ip = host
            hostname = 'Non résolu'
            mac = 'MAC inconnue'

            # Hostnames (if provided by Nmap)
            if 'hostnames' in scanner[host] and scanner[host]['hostnames']:
                hostname = scanner[host]['hostnames'][0].get('name') or resolve_hostname(ip)
            else:
                hostname = resolve_hostname(ip)

            # MAC addresses with fallback
            if 'mac' in scanner[host]['addresses']:
                mac = scanner[host]['addresses']['mac']

            from .views import get_all_local_networks
            local_networks = get_all_local_networks()
            results = None

                'ip': ip,
                form = IPNetworkForm(request.POST, local_network_choices=local_networks)
                'mac': mac
            })

                    # If a local network was selected, add it to the textarea if not already present
                    selected_local = form.cleaned_data.get('local_network')
                    if selected_local and selected_local not in networks:
                        networks.append(selected_local)


    except Exception as e:
        # Safe fallback
        return [{'error': f"Nmap scan failed on {network}: {str(e)}"}]

    return results


def scan_networks(networks):
    """Handle a list of user-submitted subnets and scan each."""

    all_results = []

                        # Update the textarea with the new list (including any added local network)
                        form = IPNetworkForm(initial={'networks': '\n'.join(networks)}, local_network_choices=local_networks)
    for network in networks:
        net = network.strip()
                form = IPNetworkForm(initial={'networks': get_local_network()}, local_network_choices=local_networks)
            continue
        try:
            ipaddress.ip_network(net)  # Will raise if invalid
            scan_result = nmap_scan(net)
            all_results.extend(scan_result)
        except ValueError:
            all_results.append({'error': f"Réseau invalide : {net}"})

    return all_results


def ip_scan_view(request):
    """
    Handle form display, scan execution (Nmap), and CSV export logic.
    """
    results = None

    if request.method == "POST":
        form = IPNetworkForm(request.POST)
        if form.is_valid():
            networks = form.cleaned_data['networks'].splitlines()

            if 'download_csv' in request.POST:
                scanned = scan_networks(networks)
                response = HttpResponse(content_type="text/csv")
                response["Content-Disposition"] = 'attachment; filename="scan_results.csv"'
                writer = csv.DictWriter(response, fieldnames=['ip', 'hostname', 'mac'])
                writer.writeheader()
                for row in scanned:
                    if 'ip' in row:  # Skip errors
                        writer.writerow(row)
                return response

            else:
                results = scan_networks(networks)
    else:
        # GET request
        form = IPNetworkForm(initial={'networks': get_local_network()})

    return render(request, 'jeyipscan/ip_scan.html', {
        'form': form,
        'results': results
    })
