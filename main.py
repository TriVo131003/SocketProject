import socket
import urllib
from urllib.parse import urlparse
import os
import bs4
import threading

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

temp_url = Url1


def conn_down(temp_url):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Fail to create socket')
    split_url = urlparse(temp_url)
    hostname = socket.gethostbyname(split_url.netloc)
    s.connect((hostname, 80))
    if(temp_url.find(
            '/', temp_url.find('/', temp_url.find('/') + 1) + 1) != -1):
        _path = temp_url[temp_url.find(
            '/', temp_url.find('/', temp_url.find('/') + 1) + 1):]
    else:
        _path = '/'
    _path = checkpath(_path)

    request = f'GET {_path} HTTP/1.1\r\nHost:{split_url.netloc}\r\nConnection: keep-alive\r\n\r\n'
    s.sendall(request.encode())
    if (temp_url.split('/')[-1] == '' and temp_url.split('/')[3] != ''):
        download_Folder(s, temp_url)
    else:
        path = ''
        if (temp_url.count('/') == 2 or (temp_url.count('/') >= 3 and temp_url.split('/')[3] == '')):
            path = 'index.html'
        elif (temp_url.split('/')[-1] != ''):
            path = temp_url.split('/')[-1]
        path = checkpath(path)
        data = getheader(s)
        if(checkContentLength(data) == 1):
            download_Chunked(s, path)
        else:
            size = getContentLength(data)
            download_Contentlength(s, path, size)

    s.close()


def getheader(s):
    data = b''
    while not data.endswith(b'\r\n\r\n'):
        data += s.recv(1)
    return data


def checkpath(path):
    temp = str(path)
    if(os.path.exists(temp)):
        if(temp.find('(') == -1 and temp.find('.') != -1):
            t1 = temp.split('.')[0]
            t2 = temp.rsplit('.')[1]
            temp = t1+'(1).'+t2
            i = 2
            while(os.path.exists(temp)):
                t1 = temp.split('(')[0]
                t2 = temp.rsplit('.')[1]
                temp = t1+'(' + str(i) + ').'+t2
                i = i + 1
        if (temp.find('.') == -1):
            temp = temp + '(1)'
            k = 2
            while(os.path.exists(temp)):
                t1 = temp.split('(')[0]
                k = k + 1
                temp = t1+'(' + str(k) + ')'
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
        return int(t2)
    return int(t1)


def checkContentLength(data):
    data_temp = data.decode()
    if(data_temp.find('Content-Length') == -1):
        return 1
    else:
        return 0


def download_Contentlength(s, path, size):
    reply = b''
    while len(reply) < size:
        _data = s.recv(1000000)
        if not _data:
            break
        reply += _data
    with open(path, 'wb') as f:
        f.write(reply)


def download_Chunked(s, path):
    response = b''
    while True:
        chunk_size = b""
        # Get the chunk size
        while not chunk_size.endswith(b'\r\n'):
            chunk_size += s.recv(1)
        # The chunk size is encoded in hex
        chunk_size = int(chunk_size[:-2].decode(), 16)
        chunk_data = b""
        chunk = s.recv(chunk_size)
        chunk_data += chunk
        cur_chunk_size = len(chunk)
        # Sometimes it won't receive all of the data
        while cur_chunk_size < chunk_size:
            chunk = s.recv(chunk_size - cur_chunk_size)
            chunk_data += chunk
            cur_chunk_size += len(chunk)
        # Receive the ending \r\n
        s.recv(2)
        # Beak when chunk_size = 0
        if not chunk_size:
            break
        response += chunk_data
        with open(path, 'wb') as f:
            f.write(response)


def download_Folder(s, temp_url):
    pathtemp = temp_url.split('/')[-2]
    pathtemp = checkpath(pathtemp)
    os.mkdir(pathtemp)
    data = getheader(s)
    size = getContentLength(data)
    reply = b''
    while len(reply) < size:
        _data = s.recv(1000000)
        if not data:
            break
        reply += _data
    data = bs4.BeautifulSoup(reply.decode(), "html.parser")
    for l in data.find_all("a"):
        if(l["href"].find('.') != -1):
            print((l["href"]))
            split_url = urlparse(temp_url + l["href"])
            if(temp_url.find(
                    '/', temp_url.find('/', temp_url.find('/') + 1) + 1) != -1):
                _path = temp_url[temp_url.find(
                    '/', temp_url.find('/', temp_url.find('/') + 1) + 1):]
            else:
                _path = '/'
            _path = _path + l["href"]
            request = f'GET {_path} HTTP/1.1\r\nHost:{split_url.netloc}\r\nConnection: keep-alive\r\n\r\n'
            s.sendall(request.encode('utf-8'))
            data = getheader(s)
            if(checkContentLength(data) != 1):
                print(1)
                size = getContentLength(data)
                reply = b''
                while len(reply) < size:
                    _data = s.recv(8192)
                    if not data:
                        break
                    reply += _data
                with open(pathtemp+'\\'+l["href"], 'wb') as f:
                    f.write(reply)
            else:
                print(2)
                response = b''
                while True:
                    chunk_size = b""
                    while not chunk_size.endswith(b'\r\n'):
                        chunk_size += s.recv(1)
                    chunk_size = int(chunk_size[:-2].decode(), 16)
                    chunk_data = b""
                    chunk = s.recv(chunk_size)
                    chunk_data += chunk
                    cur_chunk_size = len(chunk)
                    while cur_chunk_size < chunk_size:
                        chunk = s.recv(chunk_size - cur_chunk_size)
                        chunk_data += chunk
                        cur_chunk_size += len(chunk)
                    s.recv(2)
                    if not chunk_size:
                        break
                    response += chunk_data
                with open(pathtemp+'\\'+l["href"], 'wb') as f:
                    f.write(response)


#conn_down(temp_url)

# parallel
p1 = threading.Thread(target=conn_down, args=(url2,)).start()
p2 = threading.Thread(target=conn_down, args=(url5,)).start()
p3 = threading.Thread(target=conn_down, args=(url7,)).start()
