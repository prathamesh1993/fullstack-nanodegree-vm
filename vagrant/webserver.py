from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

from database_setup import Restaurant, Base, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith('/restaurants'):
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<a href= '/restaurants/new'> Make a new Restaurant here </a></br></br>"
                for x in restaurants:

                    output += "<h1> %s </h1>" % x.name
                    output += "<h4><a href='restaurants/%s/edit'>Edit</a></h4>" % x.id
                    output += "<h4><a href='restaurants/%s/delete'>Delete</a></h4>" % x.id
                    output += "</br>"

                output += "</body></html>"
                self.wfile.write(bytes(output, "UTF-8"))
                print(output)
                return

            if self.path.endswith('/new'):
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Create"> </form>'''
                output += "</body></html>"
                self.wfile.write(bytes(output, "UTF-8"))
                print(output)
                return

            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>"
                    output += myRestaurantQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/edit' >" % restaurantIDPath
                    output += "<input name = 'newRestaurantName' type='text' placeholder = '%s' >" % myRestaurantQuery.name
                    output += "<input type = 'submit' value = 'Rename'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(bytes(output, "UTF-8"))
                    print(output)
                    return

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Are you sure you want to delete %s?</h1>" % myRestaurantQuery.name

                    output += "<form method = 'POST' enctype= 'multipart/form-data' action = '/restaurants/%s/delete'> "% restaurantIDPath
                    output += "<input type = 'submit' value ='Delete'> "
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(bytes(output, "UTF-8"))
                    print(output)
                    return


        except:
            pass
    def do_POST(self):
        try:

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery:
                        session.delete(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.get('content-type'))
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantIDPath = self.path.split("/")[2]

                    myRestaurantQuery = session.query(Restaurant).filter_by(
                        id=restaurantIDPath).one()
                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = messagecontent[0]
                        session.add(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()



            if self.path.endswith('/restaurants/new'):
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')
                    output = ""
                    output += "<html><body>"
                    output += '<form method='POST' enctype='multipart/form-data' action='/restaurants'><h2>Add new restaurant</h2><input name="message" type="text" ><input type="submit" value="Create"> </form>'
                    output += "</body></html>"
                    newEntry = Restaurant(name=messagecontent[0])
                    session.add(newEntry)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location','/restaurants')
                    self.end_headers()
                    return

        except:
            pass

def main():
	try:
		port = 8090
		server = HTTPServer(('', port), webServerHandler)
		print ("Web Server running on port %s" % port)
		server.serve_forever()
	except KeyboardInterrupt:
		print (" ^C entered, stopping web server....")
		server.socket.close()

if __name__ == '__main__':
	main()
