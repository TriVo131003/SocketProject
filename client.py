
import requests
import socket
import urllib
from urllib.parse import urlparse
import os
import bs4
from http.server import HTTPServer, SimpleHTTPRequestHandler
import http.server
import hashlib
import threading
import time

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

Url1 = 'http://www.google.com'
Url2 = 'http://www.google.com/index.html'
Url3 = 'http://www.bing.com'
Url4 = 'http://anglesharp.azurewebsites.net/Chunked'
Url5 = 'http://www.httpwatch.com/httpgallery/chunked/chunkedimage.aspx'

_url1 = 'http://web.stanford.edu/class/cs224w/slides/'
_url2 = 'http://web.stanford.edu/class/cs142/lectures/'
_url3 = 'http://web.stanford.edu/class/cs143/handouts/'
_url4 = 'http://web.stanford.edu/class/cs231a/course_notes/'

# url testing

temp_url = url1

split_url = urlparse(temp_url)
hostname = socket.gethostbyname(split_url.netloc)
s.connect((hostname, 80))

# send request
request = f'GET / HTTP/1.1\r\nHost:{split_url.netloc}\r\nConnection: keep-alive\r\n\r\n'
s.sendall(request.encode())


def checkTypeDownload(temp_url):
    d = urllib.request.urlopen(temp_url)
    if (str(d.getheader('Transfer-Encoding')) == 'chunked'):
        return -1
    else:
        return 1


def download_Contentlength(temp_url, size):
    path = ''
    if (temp_url.count('/') == 2 or (temp_url.count('/') >= 3 and temp_url.split('/')[3] == '')):
        path = 'index.html'
    if (temp_url.split('/')[-1] != ''):
        path = temp_url.split('/')[-1]
    with open(path, 'wb') as f:
        str_data = ''
        while size > 0:
            datatmp = s.recv(1024)
            str_data += datatmp.decode()
            size -= len(datatmp)
        header = str_data.encode().split(b'\r\n\r\n')[0]
        content = str_data.encode()[len(header)+4:]
        f.write(content)
        print('Closing socket')
        s.close()


def checkpath(path):
    temp = str(path)
    if(os.path.exists(temp)):
        if(temp.find('(') == -1):
            print(1)
            t1 = temp.split('.')[0]
            t2 = temp.rsplit('.')[1]
            temp = t1+'(1).'+t2
            i = 2
            while(os.path.exists(temp)):
                t1 = temp.split('(')[0]
                t2 = temp.rsplit('.')[1]
                temp = t1+'(' + str(i) + ').'+t2

    return temp


def getContentLength(data):
    data_temp = data.split(b'\r\n\r\n')[0].decode()
    start = data_temp.find('Content-Length')
    t1 = data_temp[start + 16:]
    i = 0
    t2 = ''
    t = str(t1)
    if(t.find(':') != -1):
        while 1:
            if (t1[i] < '0' or t1[i] > '9'):
                break
            t2 += t1[i]
            i = i + 1
        return t2
    return int(t1)


def downloadtest(temp_url):
    g = requests.get(temp_url)
    path = ''
    if (temp_url.count('/') == 2 or (temp_url.count('/') >= 3 and temp_url.split('/')[3] == '')):
        path = 'index.html'
    if (temp_url.split('/')[-1] != ''):
        path = temp_url.split('/')[-1]
    path = checkpath(path)
    print(path)
    with open(path, 'wb') as f:
        f.write(g. content)
    data_temp = ''
    data = s.recv(1024)
    data_temp += data.decode()
    size = getContentLength(data)
    while len(data_temp) < size:
        data = s.recv(1024)
        data_temp += data.decode()
    print('Closing socket')


def download_Chunked(temp_url):
    r = requests.get(temp_url)
    path = ''
    if (temp_url.count('/') == 2 or (temp_url.count('/') >= 3 and temp_url.split('/')[3] == '')):
        path = 'index.html'
    elif (temp_url.split('/')[-1] != ''):
        path = temp_url.split('/')[-1]

    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    # data = ''
    # _data = []
    # while True:
    #     datatmp = s.recv(1024).decode('utf-8')
    #     # print(datatmp)
    #     if datatmp:
    #         #data += datatmp
    #         _data.append(datatmp)
    #     else:
    #         break
    # data = ''.join(_data)
    # # datatmp = s.recv(2048)
    # # if datatmp:
    # #     data += datatmp.decode()
    # header = data.encode().split(b'\r\n\r\n')[0]
    # content = data.encode()[len(header)+4:]
    # print(content)


def download_File(temp_url):
    if (temp_url.split('/')[-1] == '' and temp_url.split('/')[3] != ''):
        r = requests.get(temp_url)
        pathtemp = temp_url.split('/')[-2]
        os.mkdir(pathtemp)
        data = bs4.BeautifulSoup(r.text, "html.parser")
        for l in data.find_all("a"):
            if(l["href"].find('.') != -1):
                if (checkTypeDownload(temp_url + l["href"]) > 0):
                    r = requests.get(temp_url + l["href"])
                    size = checkTypeDownload(temp_url + l["href"])
                    with open(pathtemp+'\\'+l["href"], 'wb') as f:
                        str_data = ''
                        while size > 0:
                            datatmp = s.recv(1024)
                            str_data += datatmp.decode()
                            size -= len(datatmp)
                        header = str_data.encode().split(b'\r\n\r\n')[0]
                        content = str_data.encode()[len(header)+4:]
                        f.write(content)
                elif (checkTypeDownload(temp_url + l["href"]) < 0):
                    r = requests.get(temp_url + l["href"])
                    with open(pathtemp+'\\'+l["href"], 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            f.write(chunk)
                print('closing socket')
                s.close()
    elif (checkTypeDownload(temp_url) > 0):
        download_Contentlength(temp_url, checkTypeDownload(temp_url))
    elif (checkTypeDownload(temp_url) < 0):
        download_Chunked(temp_url)


downloadtest(temp_url)
# print(checkTypeDownload(temp_url))
# download_Contentlength(temp_url, checkTypeDownload(temp_url))
# download_Chunked(temp_url)
# download_File(temp_url)

# multi request
# t1 = threading.Thread(target=download_File, args=(url1,))
# t2 = threading.Thread(target=download_File, args=(url3,))
# t1.start()
# t2.start()


def download(temp_url):
    r = requests.get(temp_url)
    if (temp_url.count('/') == 2):
        with open('index.html', 'wb') as f:
            f.write(r.content)
    if (temp_url.count('/') >= 3):
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


# if (temp_url.split('/')[3] == ''):
#     with open('index.html', 'wb') as f:
#         while True:
#             for chunk in r.iter_content(chunk_size=1024):
#                 f.write(chunk)

# elif (temp_url.split('/')[-1] != ''):
#     with open(temp_url.split('/')[-1], 'wb') as f:
#         while True:
#             for chunk in r.iter_content(chunk_size=1024):
#                 if chunk:
#                     f.write(chunk)
# elif (temp_url.split('/')[-1] == '' and temp_url.split('/')[3] != ''):
#     parent_dir = "C:/Users/asus/OneDrive/Máy tính/Vscode/SocketMMT"
#     pathtemp = temp_url.split('/')[-2]
#     path = os.path.join(parent_dir, pathtemp)
#     print(path)
#     os.makedirs(path)
#     data = bs4.BeautifulSoup(r.text, "html.parser")
#     for l in data.find_all("a"):
#         if(l["href"].find('.') != -1):
#             r = requests.get(temp_url + l["href"])
#             with open(path+'\\'+l["href"], 'wb') as f:
#                 for chunk in r.iter_content(chunk_size=1024):
#                     if chunk:
#                         f.write(chunk)

# try:
#     while True:
#         if file_size <= 0:
#             break

#         data = s.recv(1024)
#         str_data += data.decode()
#         file_size -= len(data)
#     print(str_data)
# finally:
#     print('closing socket')
#     s.close()
# data = s.recv(2048)
# while(len(data) > 0):
#     print(len(data))
#     data = s.recv(2048)
# print('closing socket')
# s.close()

# chunk_size = int(line.strip().split(';')[0], 16)
