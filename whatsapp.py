           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.14/x64/lib/python3.12/site-packages/requests/api.py", line 71, in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.14/x64/lib/python3.12/site-packages/requests/sessions.py", line 635, in request
    prep = self.prepare_request(req)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.14/x64/lib/python3.12/site-packages/requests/sessions.py", line 541, in prepare_request
    p.prepare(
  File "/opt/hostedtoolcache/Python/3.12.14/x64/lib/python3.12/site-packages/requests/models.py", line 440, in prepare
    self.prepare_headers(headers)
  File "/opt/hostedtoolcache/Python/3.12.14/x64/lib/python3.12/site-packages/requests/models.py", line 570, in prepare_headers
    check_header_validity(header)
  File "/opt/hostedtoolcache/Python/3.12.14/x64/lib/python3.12/site-packages/requests/utils.py", line 1095, in check_header_validity
07/09/2026 · media 0,2212 €/kWh · 00h 🔴 0,2071 · 01h 🔴 0,2072 · 02h 🔴 0,2003 · 03h 🔴 0,2022 · 04h 🟡 0,1986 · 05h 🔴 0,2016 · 06h 🔴 0,2271 · 07h 🔴 0,2806 · 08h 🔴 0,2906 · 09h 🔴 0,2152 · 10h 🔴 0,2394 · 11h 🟡 0,1839 · 12h 🟡 0,1718 · 13h 🟡 0,1526 · 14h 🟢 0,0854 min · 15h 🟢 0,0957 · 16h 🟢 0,1034 · 17h 🟡 0,1541 · 18h 🔴 0,2802 · 19h 🔴 0,3323 · 20h 🔴 0,3703 · 21h 🔴 0,3804 max · 22h 🔴 0,2705 · 23h 🔴 0,2580 · mas baratas: 14h,15h,16h
    _validate_header_part(header, value, 1)
  File "/opt/hostedtoolcache/Python/3.12.14/x64/lib/python3.12/site-packages/requests/utils.py", line 1116, in _validate_header_part
    raise InvalidHeader(
requests.exceptions.InvalidHeader: Invalid leading whitespace, reserved character(s), or return character(s) in header value: '***'
Error: Process completed with exit code 1.
