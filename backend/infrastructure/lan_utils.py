import socket
import io
import base64
import psutil
import qrcode


def get_local_lan_ip() -> str:
    """
    Attempts to discover the primary local network (LAN) IP address.
    Falls back to 127.0.0.1 if unconnected to any LAN.
    """
    # Try UDP socket connection to a non-routable address to discover outbound route interface
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith('127.'):
            return ip
    except Exception:
        pass

    # Alternative check using network interfaces
    try:
        interfaces = psutil.net_if_addrs()
        for iface_name, addrs in interfaces.items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                    # Filter out Docker or API virtual bridges if possible
                    if not ('docker' in iface_name.lower() or 'veth' in iface_name.lower()):
                        return addr.address
    except Exception:
        pass

    return "127.0.0.1"


def get_all_network_interfaces() -> list:
    """Returns detailed list of IPv4 addresses for all active network interfaces."""
    interfaces_list = []
    try:
        interfaces = psutil.net_if_addrs()
        for iface_name, addrs in interfaces.items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interfaces_list.append({
                        "interface": iface_name,
                        "ip": addr.address,
                        "netmask": addr.netmask
                    })
    except Exception as e:
        interfaces_list.append({"interface": "unknown", "error": str(e)})
    return interfaces_list


def get_lan_hub_info(host: str = "0.0.0.0", port: int = 8000) -> dict:
    """Returns complete LAN hub deployment metadata."""
    lan_ip = get_local_lan_ip()
    local_url = f"http://localhost:{port}"
    lan_url = f"http://{lan_ip}:{port}"
    interfaces = get_all_network_interfaces()

    return {
        "hub_status": "online",
        "host": host,
        "port": port,
        "local_url": local_url,
        "lan_url": lan_url,
        "network_interfaces": interfaces
    }


def generate_qr_code_base64(data_url: str) -> str:
    """
    Generates a PNG QR code for the specified URL and returns a base64 Data URI string.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(data_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        # Fallback text representation if image generation fails
        return f"data:text/plain;charset=utf-8,{data_url}"
