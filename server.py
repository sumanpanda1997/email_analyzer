from http.server import BaseHTTPRequestHandler, HTTPServer
# from urllib.parse import urlparse, parse_qs
import cgi
import base64
import email_extractor
import email_analyzer
import email_plt
import os

class handler(BaseHTTPRequestHandler):

    def my_analyzer(self, label, duration):
        email_extractor.driver(label, duration)
        email_analyzer.driver()
        email_plt.driver()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        self.path
        # dict = parse_qs(urlparse(self.path).query)

        # if "label" in dict and "duration" in dict:
        #     label = dict["label"][0]
        #     duration = int(dict["duration"][0])
        #     print("running email email_scanner with argument -> ", label, duration)
        #     email_scanner.driver(label, duration)
        #     tfidf_classifier.driver()
        #     message = "email analysis complete"
        #     self.wfile.write(bytes(message, "utf8"))
        if self.path.endswith("/"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body><style>html{text-align: center; margin-top: 10%; font-size: 30px;}</style>"
            output += "<h1 id='hero-text'>EMAIL-ANALYZER</h1>"
            output += '''<form method='POST' 
enctype='multipart/form-data' action='/analyze'>
<h2>enter label</h2><input name="label" type="text">
<h2>enter duration</h2>
<input name="duration" type="number">
<button type="submit">Submit</form>'''
            output += "</body><script>document.getElementsByTagName('body')[0].firstChild.textContent = ''</script></html>"
            self.wfile.write(output.encode(encoding = 'utf_8'))
        if self.path.endswith("/analyze"):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            output = ""
            # output += '<html><body>&#161analyze <a href="/">Back to home</a>'
            output += '</body></html>'
            self.wfile.write(output.encode())
            print(output)

    def do_POST(self):
        # self.send_response(200)
        # self.send_header('Content-type','text/html')
        # self.end_headers()
        # form = cgi.FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD': 'POST'})
        # print form.getvalue["foo"]

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
        print("hellow beginnning post\n")
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(self.rfile, pdict)
            label = fields.get('label')
            print("label => ", label[0])
            duration = fields.get('duration')
            print("duration => ", duration[0])

        self.my_analyzer(label[0],int(duration[0]))

        base64_image_data = []
        images = os.listdir("./assets")
        
        for image in images:
            with open("./assets/" + image, "rb") as img: 
                print(img)
                encoded_data = "data:image/jpeg;base64," + base64.b64encode(img.read()).decode('utf-8')
                # self.wfile.write("<img src = " + "data:image/jpeg;base64," + str(img.read()) + ">")
                base64_image_data.append(encoded_data)
            img.close()
        output = ''
        output += '<html><style>html{text-align: center; margin-top: 10%; font-size: 30px;} img{width:30%;}</style><body>'
        output += '<h1> Your ' + label[0] + ' emails have been analyzed  for the past ' + duration[0] + ' day</h1>'
        output += '''<img id="myimage0" title="" src="" width="240" height="320">
        <img id="myimage1" title="" src="" width="240" height="320">
        <img id="myimage2" title="" src="" width="240" height="320">
<button  onclick="window.open('http://localhost:8000')" class="btn" type="button"> Back</button>'''
        output += '<script>' + generate_image_tag(base64_image_data) + '</script></body></html>'
        self.wfile.write(output.encode())

     
def generate_image_tag(base64_image_data):
    tag = ""
    i = 0
    for src in base64_image_data:
        tag = tag + "document.getElementById('myimage" + str(i) + "').src=" + "'" + src + "'" + ";"
        i += 1
    return tag


with HTTPServer(('', 8000), handler) as server:
    server.serve_forever()