import time
import os
import sys
import httplib
import urllib
import json
import datetime
import traceback

authorization_code_require_url = 'https://www.douban.com/service/auth2/auth?client_id=00821e37becbbb0901865aa73c63311b&redirect_uri=http://icek.me/callback.html&response_type=code'
authorization_code = '894d164f0d1b3993'
access_token_url = 'https://www.douban.com/service/auth2/token'

"""
while True:
        a += 1
        print a
        time.sleep(3)
        sys.stdout.flush()
"""

def get_access_token():
        params = {'client_id': '00821e37becbbb0901865aa73c63311b',
                'client_secret': '973dffdec06c1864',
                'redirect_uri': 'http://icek.me/callback.html',
                'grant_type': 'authorization_code',
                'code': authorization_code}
        params = urllib.urlencode(params)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"}
        print params
        conn = httplib.HTTPSConnection('www.douban.com')
        conn.request('POST', access_token_url, params, headers)
        response = conn.getresponse()
        print response.status, response.reason
        print response.read()
        conn.close()

def check_access_token(access_token):
        token = json.loads(access_token)
        headers = {"Authorization": "Bearer %s" % token['access_token']}
        conn = httplib.HTTPSConnection('www.douban.com')
        try:
            conn.request('GET', "https://api.douban.com/v2/user/~me", '', headers)
        except Exception as e:
            traceback.print_exc()
            return 0
        response = conn.getresponse()
        ret = int(response.status) == 200
        conn.close()
        return ret
        
def refresh_token_access_token(access_token):
        token = json.loads(access_token)
        params = {'client_id': '00821e37becbbb0901865aa73c63311b',
                'client_secret': '973dffdec06c1864',
                'redirect_uri': 'http://icek.me/callback.html',
                'grant_type': 'refresh_token',
                'refresh_token': token['refresh_token']}
        params = urllib.urlencode(params)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"}
        conn = httplib.HTTPSConnection('www.douban.com')
        conn.request('POST', access_token_url, params, headers)
        response = conn.getresponse()
        if not int(response.status) == 200:
                message(response.status)
                message(response.reason)
                message(response.read())
                conn.close()
                return None
        ret = response.read()
        conn.close()
        return ret

def message(m):
        print datetime.datetime.now(),
        print m
        sys.stdout.flush()

def main():
        access_token = json.dumps(json.load(open('access_token')))
        json.dump(json.loads(access_token), open('access_token', 'w'))
        message('access_token has write to file')
        ret = os.system('scp access_token icekme1@icek.me:www/douban_token/access_token')
        if ret != 0:
            message('WARNING: access_token SCP failed')
        else:
            message('access_token SCP successed')
        while(True):
                if not check_access_token(access_token):
                        message('WARNING: access_token expired')
                        ret = None
                        try:
                                ret = refresh_token_access_token(access_token)
                        except Exception as e:
                                traceback.print_exc()
                        if not ret:
                                message('ERROR: refresh_token failed')
                        else:
                                message('GOOD: refresh_token successed')
                                new_access_token = ret
                                json.dump(json.loads(new_access_token), open('access_token', 'w'))
                                access_token = json.dumps(json.load(open('access_token')))
                                message('access_token has write to file')
                                ret = os.system('scp access_token icekme1@icek.me:www/douban_token/access_token')
                                if ret != 0:
                                    message('WARNING: access_token SCP failed')
                                else:
                                    message('access_token SCP successed')
                else:
                        message('access_token not expired')
                time.sleep(3600)

if __name__ == '__main__':
        """
        get_access_token()
        exit(0)
        """
        while True:
            try:
                main()
            except Exception as e:
                message(e.message)
