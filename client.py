import socket
import urllib
from urllib.parse import urlparse
import os
import bs4
import threading


PORT = 80
BUFFER_SIZE = 1048576
# 1
url1 = 'http://example.com/'
url2 = 'http://example.com/index.html'
url3 = 'http://web.stanford.edu/dept/its/support/techtraining/techbriefing-media/Intro_Net_91407.ppt'
url4 = 'http://web.stanford.edu/class/cs224w/slides/01-intro.pdf'
url5 = 'http://web.stanford.edu/class/cs224w/slides/08-GNN-application.pdf'
url6 = 'http://web.stanford.edu/class/cs231a/assignments.html'
url7 = 'http://web.stanford.edu/class/cs231a/project.html'
# 2
Url1 = 'http://www.google.com'
Url2 = 'http://www.google.com/index.html'
Url3 = 'http://www.bing.com'
Url4 = 'http://anglesharp.azurewebsites.net/Chunked'
Url5 = 'http://www.httpwatch.com/httpgallery/chunked/chunkedimage.aspx'
# 3
_url1 = 'http://web.stanford.edu/class/cs224w/slides/'
_url2 = 'http://web.stanford.edu/class/cs142/lectures/'
_url3 = 'http://web.stanford.edu/class/cs143/handouts/'
_url4 = 'http://web.stanford.edu/class/cs231a/course_notes/'

URL_TEST = url1
FORMAT = 'utf-8'


def conn_down(temp_url):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Fail to create socket')

    HOST = getHost(temp_url)
    PATH = getPath(temp_url)

    # connect
    try:
        s.connect((HOST, PORT))
        print("Successful connect to " + HOST)
    except socket.error:
        print("Connection error")

    # send request
    request = f'GET {PATH} HTTP/1.1\r\nHost:{HOST}\r\nConnection: keep-alive\r\n\r\n'
    try:
        s.sendall(request.encode(FORMAT))
    except socket.error:
        print("Fail to send request")

    # parse url to down file
    if (temp_url.split('/')[-1] == '' and temp_url.split('/')[3] != ''):
        download_Folder(s, temp_url)
        print("Successfully downloaded file: " + HOST)
    else:
        path = ''
        if (temp_url.count('/') == 2 or (temp_url.count('/') >= 3 and temp_url.split('/')[3] == '')):
            path = 'index.html'
        elif (temp_url.split('/')[-1] != ''):
            path = temp_url.split('/')[-1]
        path = checkpath(path)
        data = getheader(s)
        if(checkType(data) == 0):
            download_Chunked(s, path)
            print("Successfully downloaded file: " + HOST)
        else:
            size = getContentLength(data)
            download_Contentlength(s, path, size)
            print("Successfully downloaded file: " + HOST)
    print("Closing connection: " + HOST)
    s.close()


def getPath(temp_url):
    # get _path
    if(temp_url.find(
            '/', temp_url.find('/', temp_url.find('/') + 1) + 1) != -1):
        _path = temp_url[temp_url.find(
            '/', temp_url.find('/', temp_url.find('/') + 1) + 1):]
    else:
        _path = '/'
    return _path


def getHost(temp_url):
    # parse url
    split_url = urlparse(temp_url)
    return split_url.netloc


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
                temp = t1+'(' + str(k) + ')'
                k = k + 1
    return temp


def getContentLength(data):
    data_temp = data.split(b'\r\n\r\n')[0].decode(FORMAT)
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


def checkType(data):
    data_temp = data.decode(FORMAT)
    if(data_temp.find('Transfer-Encoding: chunked') != -1):
        return 0
    elif(data_temp.find('Content-Length') != -1):
        return 1


def download_Contentlength(s, path, size):
    reply = b''
    # receive until length of data = size
    while len(reply) < size:
        _data = s.recv(BUFFER_SIZE)
        if not _data:
            break
        reply += _data
    with open(path, 'wb') as f:
        f.write(reply)


def download_Chunked(s, path):
    reply = b''
    while True:
        # get chunk_size
        temp_data_size = b""
        while not temp_data_size.endswith(b'\r\n'):
            temp_data_size += s.recv(1)
        # decode chunked size in hex
        chunk_size = int(temp_data_size[:-2].decode(), 16)
        # get data with chunk_size
        chunk_data = b""
        chunk_data += s.recv(chunk_size)
        # use in case: length data < chunked size
        cur_chunk_size = len(chunk_data)
        while cur_chunk_size < chunk_size:
            _data = s.recv(chunk_size - cur_chunk_size)
            chunk_data += _data
            cur_chunk_size += len(_data)
        # receive \r\n
        s.recv(2)
        reply += chunk_data
        if not chunk_size:
            break
        with open(path, 'wb') as f:
            f.write(reply)


def download_Folder(s, temp_url):
    pathtemp = temp_url.split('/')[-2]
    pathtemp = checkpath(pathtemp)
    os.mkdir(pathtemp)
    try:
        data = getheader(s)
    except socket.error:
        print("Fail to receive data")
    reply = b''
    # check type for receive data

    # content-length
    if(checkType(data) == 1):
        size = getContentLength(data)
        while len(reply) < size:
            _data = s.recv(BUFFER_SIZE)
            if not data:
                break
            reply += _data
    # chunked encoding
    else:
        reply = b''
        while True:
            # get chunk_size
            temp_data_size = b""
            while not temp_data_size.endswith(b'\r\n'):
                temp_data_size += s.recv(1)
            # decode chunked size in hex
            chunk_size = int(temp_data_size[:-2].decode(), 16)
            # get data with chunk_size
            chunk_data = b""
            chunk_data += s.recv(chunk_size)
            # use in case: length data < chunked size
            cur_chunk_size = len(chunk_data)
            while cur_chunk_size < chunk_size:
                _data = s.recv(chunk_size - cur_chunk_size)
                chunk_data += _data
                cur_chunk_size += len(_data)
            # receive \r\n
            s.recv(2)
            reply += chunk_data
            if not chunk_size:
                break

    # parse data
    data = bs4.BeautifulSoup(reply.decode(FORMAT), "html.parser")
    # find <a>...</a>
    for l in data.find_all("a"):
        # find name file for download
        if(l["href"].find('.') != -1):
            print((l["href"]))
            host = getHost(temp_url + l["href"])
            _path = getPath(temp_url + l["href"])
            # send request
            request = f'GET {_path} HTTP/1.1\r\nHost:{host}\r\nConnection: keep-alive\r\n\r\n'
            try:
                s.sendall(request.encode(FORMAT))
            except socket.error:
                print("Fail to send request")
            # get header
            data = getheader(s)
            if(checkType(data) == 1):
                size = getContentLength(data)
                reply = b''
                while len(reply) < size:
                    _data = s.recv(BUFFER_SIZE)
                    if not data:
                        break
                    reply += _data
                with open(pathtemp+'\\'+l["href"], 'wb') as f:
                    f.write(reply)
            else:
                reply = b''
                while True:
                    # get chunk_size
                    temp_data_size = b""
                    while not temp_data_size.endswith(b'\r\n'):
                        temp_data_size += s.recv(1)
                    # decode chunked size in hex
                    chunk_size = int(temp_data_size[:-2].decode(), 16)
                    # get data with chunk_size
                    chunk_data = b""
                    chunk_data += s.recv(chunk_size)
                    # use in case: length data < chunked size
                    cur_chunk_size = len(chunk_data)
                    while cur_chunk_size < chunk_size:
                        _data = s.recv(chunk_size - cur_chunk_size)
                        chunk_data += _data
                        cur_chunk_size += len(_data)
                    # receive \r\n
                    s.recv(2)
                    reply += chunk_data
                    if not chunk_size:
                        break
                with open(pathtemp+'\\'+l["href"], 'wb') as f:
                    f.write(reply)


if __name__ == "__main__":
    threads = []
    print("Enter URL or URLs")
    url_in = input()
    url_list = url_in.split(' ')
    for url in url_list:
        print(getHost(url))
        threads.append(threading.Thread(
            target=conn_down, args=(url,)).start())
