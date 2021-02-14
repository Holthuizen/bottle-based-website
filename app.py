from bottle import route, run, template, SimpleTemplate, view, TEMPLATE_PATH, request, response, redirect, get, post
#security 
import secrets
import hashlib

#add template dir to path
TEMPLATE_PATH.insert(0, 'views')

#a random secret every time the server reboots
secret = secrets.token_bytes(12)
#users that have a account
users ={'test':"pass","user2":"pass"}
#logged in users
authorized = {}
#base url
server_url = "http://localhost:8080"





@route('/')
@view('template_one')
def index():
    return dict(path= server_url, title="hallo world",admin=False)


## add a input method, that encrypts or hashes the username and password on the client. than compair that to a hash of the store pw on the server

#view 
@get('/login')
def login():
    return template('login')


#view
@route("/admin")
@view('template_one')
def admin(): 
    #read cookies
    user = request.get_cookie("user", secret=secret)
    token = request.get_cookie("token", secret=secret)
    
    #defensive approach, if any of the tests fail terminate 
    if not (user and token): 
        print("You are not yet logged in, no token pressend")
        return redirect(server_url + "/login")
    
    if not (user in authorized):
        print("You are not yet logged in, no token pressend")
        return redirect(server_url + "/login")

    #check if token token of cookie == token in authorized[username]
    if authorized[user] != token:
        return "You are not yet logged in, no token pressend"
    return dict(path=server_url, title="Admin area, restricted access",admin=True)    




#logic
@post('/login')
def login():
    postdata = request.body.read()
    username = request.forms.get("username")
    pw = request.forms.get("password")

    if not username in users:
        print("username or password incorrect")
        return redirect(server_url + "/login")

    #auth
    if users[username] == pw: 

        #generate random token, string of hex values, size 16 chars
        token = hashlib.sha256(secrets.token_bytes(12) + pw.encode()).hexdigest()[:16]

        #sha3 hash username for anonymity, used as identifier/key
        hashed_username = hashlib.sha3_256(username.encode()).hexdigest()[:16]

        #add username and token to logedin in dir
        authorized[hashed_username] = token

        #store token in cookie.
        """
        limit cookie to /admin paths. 
        cookies are signed with server secret
        """    
        cookie_config = dict(path='/admin', httponly=True, samesite="strict", secret=secret)
        response.set_cookie("user",hashed_username,**cookie_config)
        response.set_cookie("token",token, **cookie_config)
        
        return redirect(server_url + "/admin")



#logic
@route("/admin/logout")
def logout():
    #read cookies
    user = request.get_cookie("user", secret=secret)
    token = request.get_cookie("token", secret=secret)
    
    #send command to client browser to remove the cookies
    if user: 
        response.delete_cookie("user",path='/admin',secret=secret)
        #remove entry from dict. 
        del authorized[user]

    if token: 
        response.delete_cookie("token",path='/admin',secret=secret)
    
    #return template("Logged out as {{user}} with token {{token}}",user=user,token=token) 
    return redirect(server_url + "/admin")


run(host='localhost', port=8080, debug=True, reload=True)