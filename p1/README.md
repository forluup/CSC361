### P1 - SmartClient.py
---
Given the URL of web server, SmartClient outputs the following information:
1. hostname
2. http2 support
3. received status code or redirect link if redirect occurs
4. list of cookies (if there are any)
5. whether or not the website is password-protected

**Usage:**
`python3 SmartClient.py <url>`

**URL formats supported:**
- https://example.com
- https://example.com/path/file
- https://\<valid IP address\>
- www.example.com
- example.com

**Example Usage:**
`❯ python3 SmartClient.py https://uvic.ca`

**Output:**
```
Website: uvic.ca
1. Supports http2: no
Redirecting to: https://www.uvic.ca/
Request succeeded.
2. List of Cookies:
cookie name: PHPSESSID
cookie name: uvic_bar, expires time: Thu, 01-Jan-1970 00:00:01 GMT; , domain name: .uvic.ca
cookie name: www_def
cookie name: TS018b3cbd
cookie name: TS0165a077, domain name: .uvic.ca
3. Password-protected: no
```

**Example Usage 2:**
`❯ python SmartClient.py https://google.com`

**Output:**
```
Website: google.com
1. Supports http2: yes
Received status code: 301
1. List of Cookies:
2. Password-protected: no
```