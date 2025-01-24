import socket
import ssl
import sys


def check_http2_support(host, port=443):
    """Check if the server supports HTTP/2."""
    context = ssl.create_default_context()
    context.set_alpn_protocols(['http/1.1', 'h2'])  # Enable ALPN for HTTP/1.1 and HTTP/2

    with context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host) as conn:
        try:
            conn.connect((host, port))  # Connect to the host on port 443
            selected_protocol = conn.selected_alpn_protocol()
            return selected_protocol == 'h2'  # Return True if HTTP/2 is supported
        except Exception as e:
            print(f"Error checking HTTP/2 support: {e}")
            return False


def fetch_http_response(host, port=80, path="/"):
    """Fetch an HTTP response from the given host."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))  # Connect to the server
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            s.send(request.encode())  # Send the GET request
            response = s.recv(4096)  # Receive the response
            return response.decode()
    except Exception as e:
        print(f"Error fetching HTTP response: {e}")
        return None


def fetch_https_response(host, path="/"):
    """Fetch an HTTPS response using an SSL-wrapped socket."""
    context = ssl.create_default_context()
    try:
        with context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host) as conn:
            conn.connect((host, 443))  # Connect to the server on port 443
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            conn.send(request.encode())  # Send the GET request
            response = conn.recv(4096)  # Receive the response
            return response.decode()
    except Exception as e:
        print(f"Error fetching HTTPS response: {e}")
        return None


def main():
    """Main function to test the WebTester."""
    # Ensure a URL is passed as an argument
    if len(sys.argv) != 2:
        print("Usage: python WebTester.py <website_url>")
        sys.exit(1)

    url = sys.argv[1].strip()

    # Parse the URL
    if url.startswith("https://"):
        protocol = "https"
        port = 443
        host = url.replace("https://", "").split("/")[0]
    elif url.startswith("http://"):
        protocol = "http"
        port = 80
        host = url.replace("http://", "").split("/")[0]
    else:
        print("Invalid URL. Please include http:// or https://")
        sys.exit(1)

    # Check HTTP/2 support
    supports_http2 = check_http2_support(host, port) if protocol == "https" else False

    # Fetch the response
    if protocol == "https":
        response = fetch_https_response(host)
    else:
        response = fetch_http_response(host)

    # Output the results
    print("\n--- Results ---")
    print(f"Website: {url}")
    print(f"1. Supports HTTP/2: {'yes' if supports_http2 else 'no'}")

    if response:
        print("\n--- Response ---")
        print(response)


if __name__ == "__main__":
    main()
