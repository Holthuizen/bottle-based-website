from bottle import route, run, template, SimpleTemplate, view, TEMPLATE_PATH, request, response, redirect
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
    return dict(title="hallo world",admin=False)


@route('/login/<username>/<pw>')
def login(username,pw):
    if username in users:
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


@route("/admin")
@view('template_one')
def admin(): 
    #read cookies
    user = request.get_cookie("user", secret=secret)
    token = request.get_cookie("token", secret=secret)
    
    #defensive approach, if any of the tests fail terminate 
    if not (user and token): 
        return "You are not yet logged in, no token pressend"
    
    if not (user in authorized):
        return "You are not yet logged in, no token pressend"
           
    #check if token token of cookie == token in authorized[username]
    if authorized[user] != token:
        return "You are not yet logged in, no token pressend"
    
    return dict(title="Admin area, restricted access",admin=True)




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
    return template('template_one',title="Logged out successfully",admin=False)

run(host='localhost', port=8080, debug=True, reload=True)