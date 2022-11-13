
import requests
import socket
import urllib
from urllib.parse import urlparse
import os
import bs4

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Fail to create socket')
url1 = 'http://example.com/'
url2 = 'http://example.com/index.html'
url3 = 'http://web.stanford.edu/dept/its/support/techtraining/techbriefing-media/Intro_Net_91407.ppt'
url4 = 'http://web.stanford.edu/class/cs224w/slides/01-intro.pdf'
url5 = 'http://web.stanford.edu/class/cs224w/slides/08-GNN-application.pdf'
url6 = 'http://web.stanford.edu/class/cs231a/assignments.html'
url7 = 'http://web.stanford.edu/class/cs231a/project.html'

url8 = 'http://web.stanford.edu/class/cs224w/slides/'
temp_url = url8
split_url = urlparse(temp_url)
hostname = socket.gethostbyname(split_url.netloc)
s.connect((hostname, 80))
request = f'GET / HTTP/1.1\r\nHost:www.{split_url.netloc}\r\nConnection: keep-alive\r\n\r\n'
s.send(request.encode())

# d = urllib.request.urlopen(temp_url)
# file_size = int(d.getheader('Content-Length'))

r = requests.get(temp_url)
if (temp_url.split('/')[3] == ''):
    with open('index.html', 'wb') as f:
        f.write(r.content)
elif (temp_url.split('/')[-1] != ''):
    with open(temp_url.split('/')[-1], 'wb') as f:
        f.write(r.content)
elif (temp_url.split('/')[-1] == '' and temp_url.split('/')[3] != ''):
    parent_dir = "C:/Users/asus/OneDrive/Máy tính/Vscode/SocketMMT"
    pathtemp = temp_url.split('/')[-2]
    path = os.path.join(parent_dir, pathtemp)
    print(path)
    os.makedirs(path)
    data = bs4.BeautifulSoup(r.text, "html.parser")
    for l in data.find_all("a"):
        if(l["href"].find('.') != -1):
            r = requests.get(temp_url + l["href"])
            with open(path+'\\'+l["href"], 'wb') as f:
                f.write(r.content)

    # if (url1.split('/')[3] == ''):
    #     with open('index.html', "wb") as Pypdf:
    #         for chunk in s.iter_content(chunk_size=1024):
    #             if chunk:
    #                 Pypdf.write(chunk)
    # elif (url1.split('/')[-1] != ''):
    #     with open('', "wb") as Pypdf:
    #         for chunk in s.iter_content(chunk_size=1024):
    #             if chunk:
    #                 Pypdf.write(chunk)

# str_data = ''
# try:
#     while True:
#         if file_size <= 0:
#             break

#         data = s.recv(1024)
#         str_data += data.decode()
#         file_size -= len(data)
# finally:
#     print('closing socket')
#     s.close()
