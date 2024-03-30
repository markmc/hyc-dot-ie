
import os
import os.path
import urllib.parse
import json
from lxml import html

URL_BASE = 'https://hyc.ie'
USERNAME = os.environ.get('ADMIN_USERNAME')
PASSWORD = os.environ.get('ADMIN_PASSWORD')

def login(session):
    result = session.get(URL_BASE + "/login")
    tree = html.fromstring(result.text)
    authenticity_token = tree.xpath("//input[@name='authenticity_token']/@value")[0]

    payload = {
        'authenticity_token': authenticity_token,
        'user_session[login]': USERNAME,
        'user_session[password]': PASSWORD,
    }

    return session.post(URL_BASE + "/login", data=payload)

def get_resources_page(session, url):
    resources_text = session.get(URL_BASE + url).text
    tree = html.fromstring(resources_text)
    resources = []
    for row in tree.xpath("//tr[@class='odd' or @class='even']"):
        resource = {}
        resource['url'] = row.xpath('.//td[2]/a/@href')[0]
        resource['name'] = row.xpath('.//td[2]/a/text()')[0]
        resource['filename'] = row.xpath('.//td[3]/text()')[0]
        resource['mimetype'] = row.xpath('.//td[4]/text()')[0]
        resource['date'] = row.xpath('.//td[5]/text()')[0]
        resource['download_url'] = row.xpath('.//td[6]/a[contains(@class, "inline_download_icon")]/@href')[0]
        resources.append(resource)
    next_hrefs = tree.xpath("//a[@rel='next']/@href")
    return (resources, next_hrefs[0] if len(next_hrefs) > 0 else None)

def get_resources(session):
    resources, next_url = get_resources_page(session, "/admin/resources")
    while next_url:
        next_resources, next_url = get_resources_page(session, next_url)
        resources.extend(next_resources)
    return resources

def get_file(session, url, directory):
    filename = os.path.basename(url)
    if "?" in filename:
        filename = filename.split("?")[0]
    path = os.path.join(directory, filename)
    if not os.path.exists(path):
        print(f"Downloading {path}")
        r = session.get(URL_BASE + url)
        open(path, 'wb').write(r.content)
    else:
        print(f"Skipping {path}")

def write_metadata(objects, directory):
    s = json.dumps(objects)
    open(os.path.join(directory, 'metadata.json'), 'w').write(s)
