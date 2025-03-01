import socket
import ssl
import sys
import re
from urllib.parse import urlparse, urljoin


def check_http2_support(host, port=443):
    # check if host supports HTTP/2 using ALPN.
    context = ssl.create_default_context()
    context.set_alpn_protocols(['http/1.1', 'h2'])
    try:
        with context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host) as conn:
            conn.connect((host, port))
            selected_protocol = conn.selected_alpn_protocol()
            return selected_protocol == 'h2'  # return true if HTTP/2 is supported
    except Exception as e:
        print(f"Error checking HTTP/2 support: {e}")
        return False

def send_request(host, port, request):
    # send a request to the given host and port, and receive the response.
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
    # fetch HTTPS response using SSL-wrapped socket, and handle redirects.
    context = ssl.create_default_context()
    redirect_count = 0

    while True:
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
                response = response.decode()

                # extract status code
                status_line = response.split("\r\n")[0]
                status_code = int(status_line.split(" ")[1])

                # handle redirects
                if status_code == 302:
                    redirect_count += 1
                    # extract header for the new URL
                    headers = response.split("\r\n")
                    location = None
                    for header in headers:
                        if header.lower().startswith("location:"):
                            location = header.split(":", 1)[1].strip()
                            break
                    if not location:
                        print("Redirect location not found.")
                        return None, None

                    # parse the new URL and update host and path
                    parsed_location = urlparse(location)
                    host = parsed_location.netloc or host  # use the same host if netloc is empty
                    path = parsed_location.path or "/"
                    print(f"Redirecting to: {location}")
                    continue

                # handle other status codes
                if status_code == 200:
                    print("Request succeeded.")
                elif status_code == 404:
                    print("Error: 404 Not Found")
                elif status_code == 505:
                    print("Error: 505 HTTP Version Not Supported")
                else:
                    print(f"Received status code: {status_code}")

                return response, request

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
    # check if site is password protected from response
    try:
        if "401 Unauthorized" in response or "403 Forbidden" in response:
            return True
    except Exception as e:
        print(f"Error checking password protection: {e}")
    return False

def parse_url(url):
    # parse URL to get host and path
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url  # assume HTTPS if no protocol is provided

    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path if parsed.path else "/"

    return host, path

def main():
    # ensure a URL is passed as argument
    if len(sys.argv) != 2:
        print("Usage: python3 SmartClient.py <website_url>")
        sys.exit(1)

    url = sys.argv[1].strip()

    # parse URL to extract host and path
    host, path = parse_url(url)
    print(f"Website: {host}")

    # check HTTP/2 support 
    supports_http2 = check_http2_support(host)
    print(f"1. Supports http2: {'yes' if supports_http2 else 'no'}")

    # fetch HTTPS response
    response, request = fetch_https_response(host, path)

    if response:
        # extract cookies
        pattern_expires = re.compile(r"([Ee]xpires=)(\S+.\S+.\S+.\S+.)")
        cookies = extract_cookies(response)
        print("2. List of Cookies:")
        for cookie in cookies:
            cookie_parts = cookie.split(";")
            cookie_name = cookie_parts[0].split("=")[0].strip()
            cookie_domain = None
            if pattern_expires.search(cookie) is not None:
                expires = pattern_expires.search(cookie).group(2)
            else:
                expires = None
            for part in cookie_parts:
                if "domain=" in part:
                    cookie_domain = part.split("=")[1].strip()

            output = f"cookie name: {cookie_name}"
            if expires:
                output += f", expires time: {expires}"
            if cookie_domain:
                output += f", domain name: {cookie_domain}"
            print(output)
        
        # check for password protection
        password_protected = check_password_protection(response)
        print(f"3. Password-protected: {'yes' if password_protected else 'no'}")

    else:
        print("Failed to fetch a response.")


if __name__ == "__main__":
    main()