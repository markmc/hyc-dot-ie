
import os
import os.path
import urllib.parse
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
    resources = session.get(URL_BASE + url)
    tree = html.fromstring(resources.text)
    resources_hrefs = tree.xpath("//a[@class='inline_download_icon']/@href")
    next_hrefs = tree.xpath("//a[@rel='next']/@href")
    return (resources_hrefs, next_hrefs[0] if len(next_hrefs) > 0 else None)

def get_resources(session):
    resources_hrefs, next_url = get_resources_page(session, "/admin/resources")
    while next_url:
        hrefs, next_url = get_resources_page(session, next_url)
        resources_hrefs.extend(hrefs)
    return resources_hrefs

def get_file(session, url, directory):
    r = session.get(URL_BASE + url)
    filename = os.path.basename(url)
    if "?" in filename:
        filename = filename.split("?")[0]
    open(os.path.join(directory, filename), 'wb').write(r.content)
