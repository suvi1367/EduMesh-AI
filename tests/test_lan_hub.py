import pytest
from backend.infrastructure.lan_utils import (
    get_local_lan_ip,
    get_all_network_interfaces,
    get_lan_hub_info,
    generate_qr_code_base64
)


def test_get_local_lan_ip():
    ip = get_local_lan_ip()
    assert isinstance(ip, str)
    assert len(ip) > 0
    # Basic IPv4 format validation
    parts = ip.split(".")
    assert len(parts) == 4
    for p in parts:
        assert p.isdigit()


def test_get_all_network_interfaces():
    ifaces = get_all_network_interfaces()
    assert isinstance(ifaces, list)
    for iface in ifaces:
        assert "interface" in iface


def test_get_lan_hub_info():
    info = get_lan_hub_info(host="0.0.0.0", port=8000)
    assert info["hub_status"] == "online"
    assert info["host"] == "0.0.0.0"
    assert info["port"] == 8000
    assert "http://localhost:8000" in info["local_url"]
    assert "http://" in info["lan_url"]
    assert isinstance(info["network_interfaces"], list)


def test_generate_qr_code_base64():
    url = "http://192.168.1.50:8000"
    qr_uri = generate_qr_code_base64(url)
    assert isinstance(qr_uri, str)
    assert qr_uri.startswith("data:")
    assert "base64," in qr_uri or "charset=" in qr_uri
