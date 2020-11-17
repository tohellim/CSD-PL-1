from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server
import json
import datetime
import pytz
from tzlocal import get_localzone

all_tz = pytz.all_timezones

def time_handler(tz = get_localzone(),date = pytz.utc.localize(datetime.datetime.utcnow())):
    if date is time_handler.__defaults__[1]:
        return date.astimezone(tz)
    if date is not time_handler.__defaults__[1]:
        return tz.localize(date)
    
def time_app(environ, start_response):
    setup_testing_defaults(environ)

    if environ['REQUEST_METHOD'] == 'GET':
        if environ['PATH_INFO'] == '/':

            headers = [('Content-type', 'text/html; charset=utf-8')]
            start_response('200 OK', headers)
            return [(
                    '''<body>
                        <h2>LOCAL TIME</h2>
                        <time>''' +str(time_handler())[:16]+ '''</time>
                    </body> '''
                        ).encode()]
        
        
        if environ['PATH_INFO'][1:] in all_tz:

            status = '200 OK'
            headers = [('Content-type', 'text/html; charset=utf-8')]
            start_response(status, headers)            
            required_tz = pytz.timezone(environ['PATH_INFO'][1:])
            return [(
                    '''<body>
                        <h2>''' + environ['PATH_INFO'][1:] + '''</h2>
                        <time>''' +str(time_handler(required_tz))[:16]+ '''</time>
                    </body> '''
                        ).encode()]
        else:
            
            status = '404 NOT FOUND'
            headers = [('Content-type', 'text/html; charset=utf-8')]
            start_response(status, headers)  

            return [(
                    '''<body>
                        <h2>WRONG TZ</h2>
                        <h3>TZ LIST:</h3>
                        <time>''' +str(all_tz)+ '''</time>
                    </body> '''
                        ).encode("utf-8")]
        
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except (ValueError):
                request_body_size = 0

            request_body = environ['wsgi.input'].read(request_body_size)
            body = json.loads(request_body)
        except:
            headers = [('Content-type', 'application/json; charset=utf-8')]
            start_response('404 NOT FOUND', headers)
            data = json.dumps({"Eror:":'DATA NOT FOUND'})
            return data.encode().splitlines()

        if environ['PATH_INFO'] == '/api/v1/date':
            try:
                tz = body['tz']
            except:
                headers = [('Content-type', 'application/json; charset=utf-8')]
                start_response('200 OK', headers) 
                data = json.dumps({"Answer:":str(time_handler())[:10]})
                return data.encode().splitlines()
            if tz in all_tz:
                headers = [('Content-type', 'application/json; charset=utf-8')]
                start_response('200 OK', headers)
                required_tz = pytz.timezone(tz)
                data = json.dumps({"Answer:":str(time_handler(required_tz))[:10]})
                return data.encode().splitlines()
            else:
                headers = [('Content-type', 'application/json; charset=utf-8')]
                start_response('404 NOT FOUND', headers)
                data = json.dumps({"Eror:":'tz not found'})
                return data.encode().splitlines()

        if environ['PATH_INFO'] == '/api/v1/time':
            try:
                tz = body['tz']
            except:
                headers = [('Content-type', 'application/json; charset=utf-8')]
                start_response('200 OK', headers)
                data = json.dumps({"Answer:":str(datetime.datetime.time(time_handler()))[:8]})
                return data.encode().splitlines()
            
            if tz in all_tz:
                    headers = [('Content-type', 'application/json; charset=utf-8')]
                    start_response('200 OK', headers)
                    required_tz = pytz.timezone(tz)
                    data = json.dumps({"Answer:":str(datetime.datetime.time(time_handler(required_tz)))[:8]})
                    return data.encode().splitlines()
            else:
                headers = [('Content-type', 'application/json; charset=utf-8')]
                start_response('404 NOT FOUND', headers)
                data = json.dumps({"Eror:":'tz not found'})
                return data.encode().splitlines()

                    
        if environ['PATH_INFO'] == '/api/v1/datediff':
            try:
                start_date = datetime.datetime.strptime(body['start']['date'], '%m.%d.%Y %H:%M:%S')
                if 'tz' in body['start']:
                    start_tz = pytz.timezone(body['start']['tz'])
                    start_date = time_handler(start_tz,start_date)
                else:
                    start_date = time_handler(date = start_date)
                
                end_date = datetime.datetime.strptime(body['end']['date'], '%m.%d.%Y %H:%M:%S')
                if 'tz' in body['end']:
                    end_tz = pytz.timezone(body['end']['tz'])
                    end_date = time_handler(end_tz,end_date)
                else:
                    end_date = time_handler(date=end_date)
            except:
                headers = [('Content-type', 'application/json; charset=utf-8')]
                start_response('404 NOT FOUND', headers)
                data = json.dumps({"Eror:":'BAD DATA'})
                return data.encode().splitlines()
            
            delta = start_date - end_date
            headers = [('Content-type', 'application/json; charset=utf-8')]
            start_response('200 OK', headers)
            data = json.dumps({"Answer:": str(delta)})
            return data.encode().splitlines()

        else:
            headers = [('Content-type', 'application/json; charset=utf-8')]
            start_response('404 NOT FOUND', headers)
            data = json.dumps({"Eror:":'API NOT FOUND'})
            return data.encode().splitlines()


with make_server('', 8080, time_app) as httpd:
    print("Serving on port 8080...")
    httpd.serve_forever()
            
        

        