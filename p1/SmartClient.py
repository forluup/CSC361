import socket
import ssl
import sys
import re
from urllib.parse import urlparse


def check_http2_support(host, port=443):
    """Check if the host supports HTTP/2 using ALPN."""
    context = ssl.create_default_context()
    context.set_alpn_protocols(['http/1.1', 'h2'])  # Enable HTTP/1.1 and HTTP/2 protocols
    try:
        with context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host) as conn:
            conn.connect((host, port))
            selected_protocol = conn.selected_alpn_protocol()
            return selected_protocol == 'h2'  # Return True if HTTP/2 is supported
    except Exception as e:
        print(f"Error checking HTTP/2 support: {e}")
        return False


def send_request(host, port, request):
    """Send a request to the given host and port, and receive the response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.send(request.encode())
            response = b""
            while True:
                data = s.recv(10000)
                if not data:
                    break
                response += data
            return response.decode()
    except Exception as e:
        print(f"Error sending request: {e}")
        return None


def fetch_https_response(host, path="/"):
    """Fetch an HTTPS response using an SSL-wrapped socket."""
    context = ssl.create_default_context()
    try:
        with context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host) as conn:
            conn.connect((host, 443))
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            conn.send(request.encode())
            response = b""
            while True:
                data = conn.recv(10000)
                if not data:
                    break
                response += data
            return response.decode(), request
    except Exception as e:
        print(f"Error fetching HTTPS response: {e}")
        return None, None


def extract_cookies(response):
    cookies = []
    try:
        headers = response.split("\r\n")
        for header in headers:
            if header.lower().startswith("set-cookie:"):
                cookie = header.split(":", 1)[1].strip()
                cookies.append(cookie)
    except Exception as e:
        print(f"Error extracting cookies: {e}")
    return cookies

def check_password_protection(response):
    """Check if the site is password-protected based on the response."""
    try:
        if "401 Unauthorized" in response or "403 Forbidden" in response:
            return True
    except Exception as e:
        print(f"Error checking password protection: {e}")
    return False


def main():
    """Main function for the SmartClient."""
    # Ensure a URL is passed as an argument
    if len(sys.argv) != 2:
        print("Usage: python3 SmartClient.py <website_url>")
        sys.exit(1)

    url = sys.argv[1].strip()

    # Validate and parse URL
    if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', url):
        print("Invalid URL format. Example: uvic.ca, google.ca")
        sys.exit(1)

    host = url
    print(f"website: {host}")

    # HTTP/2 Support Check
    supports_http2 = check_http2_support(host)
    print(f"1. Supports http2: {'yes' if supports_http2 else 'no'}")

    # Fetch HTTPS response
    response, request = fetch_https_response(host)

    if response:
        # Extract cookies
        pattern_expires = re.compile(r"([Ee]xpires=)(\S+.\S+.\S+.\S+.)")
        cookies = extract_cookies(response)
        print("2. List of Cookies:")
        for cookie in cookies:
            cookie_parts = cookie.split(";")
            cookie_name = cookie_parts[0].split("=")[0].strip()
            cookie_domain = "domain not found"
            if pattern_expires.search(cookie) is not None:
                expires = pattern_expires.search(cookie).group(2)
            else:
                expires = None
            for part in cookie_parts:
                if "domain=" in part:
                    cookie_domain = part.split("=")[1].strip()
            if expires is not None:
                print(f"cookie name: {cookie_name}, expires time: {expires}domain name: {cookie_domain}")
            else:
                print(f"cookie name: {cookie_name}, domain name: {cookie_domain}")

        # Check for password protection
        password_protected = check_password_protection(response)
        print(f"3. Password-protected: {'yes' if password_protected else 'no'}")

    else:
        print("Failed to fetch a response.")


if __name__ == "__main__":
    main()
