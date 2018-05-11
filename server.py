from flask import Flask, session, request, redirect, render_template, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re
app=Flask(__name__)
app.secret_key='aiugf7tfg7agufbia'
bcrypt = Bcrypt(app)
app.secret_key='Fg5g45wg5wgw4545ufghfgfftyt5'
mysql = connectToMySQL('wall-db')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
print('\n','= = = server start = = = server.py ')


@app.route('/')
def index():
    print('------ inside /')
    return render_template('index.html')

# ========================================== LOGIN =========================
@app.route('/login', methods=['post'])
def login():
    print("\n @@@@@@@@ SERVER > LOGIN : POST DATA - EMAIL: ")
    print('=========== inside login ==========')
    # grab the email request.form['emmail']
    # grab the password request.form['password']
    
    #give data to send to the query
    data = { "email" : request.form["email"]}
    # create a query to find a record in the DB with the email and password\
    query = "SELECT * FROM users WHERE email = %(email)s;"
    # run the query, and return an array of matches
    find_result = mysql.query_db(query, data)
    if find_result:
        if bcrypt.check_password_hash(find_result[0]['password'], request.form['password']):
            # session the id
            session['id'] = find_result[0]['id']
            session['name'] = find_result[0]['name']
            print('@@@@@@ id is = ', session['id'])
            print('@@@@@@ name is = ', session['name'])
    
    # if len(results) > 0: # other way of saying if result:
        # if matches existed, result is an array of objects
        print('\n',"Something was returned from the DB")
        print('\n query-results = ', find_result) # array of objects (possibly only 1 returned)
        print('\n query-results[0] = ',find_result[0]) # the first object in the array
        print('\n query-results[0][id] = ',find_result[0]['id']) # the first objec'ts id key in the array
        print('\n')
        # session['id'] = results[0]['id']
        # session['name'] = results[0]['name']
        # redirect to the wall
        return redirect('/wall')

    else: 
        flash('could not log in - try again',"login")
        # did not match, result is an empty array
        print("Nothing was found in the DB")
    
    print('===== inside login')
    return redirect('/')

# ========================================== REGISTRATION ====================
@app.route('/registration', methods=['post'])
def registration():
    print("SERVER > REGISTRATION : POST DATA: ")
    print('=========== inside registration ===========')
    # print(form.request['name'])
    # ------ from other
    errorValidation = False

    # --------------  NAME
    if request.form['name'] == '':
        print('@@@@@@ name is empty')
        flash('Name cannot be empty', 'register')
        errorValidation = True
    if len(request.form['name']) < 2:
        print('@@@@@@@@@ name is LESS than 2 char') 
        flash('Name must have AT LEAST 2 letters', 'register')
        errorValidation = True
    if request.form['name'].isalpha() == False:
        print('@@@@@@@@@@ name is not a string')
        flash('Name must contain ONLY letters', 'register')
        errorValidation = True

    #-------------- EMAIL
    if len(request.form['email']) < 1:
        print('@@@@@@ email is blank!')
        flash('email cannot be blank!', 'register')
        errorValidation = True
    elif not EMAIL_REGEX.match(request.form['email']):
        print('@@@@@@ invalid chars on email')
        flash('invalid email address!', 'register')
        errorValidation = True

    #grab the request.form['email'] and put it in an obj to send to the query
    data_email={
        "email": request.form['email']
    }
    # check to see if email entered is in the DB by running a query to return back to us
    #make a query to find a record in the DB with the email
    query1="SELECT email FROM users WHERE email=%(email)s;"
    #run the query and return an array of matches
    result_email=mysql.query_db(query1, data_email)
    print('@@@@@@@@ result email is --> ',result_email) #show if it returns the same email from the db
    print('@@@@@@@@ query1 is : ',query1)
    # if an array exists that means a data point w/ that email exists 
    if len(result_email) > 0:
        flash('cannot use this email','register')
        print('@@@@@@ we found a match!!!!! DO NOT REGISTER')
        errorValidation = True
    else:
        print('@@@@@@ No match, go ahead and register user')

    # ------------- PW VALIDATION
    if len(request.form['password']) == 0:
        print('@@@@@@ PW cannot be blank!')
        flash('@@@@@ PW cannot be blank!','register')
        errorValidation = True
        # print(errorValidation)
    if len(request.form['password']) <3:
        print('@@@@@@ PW is less than 3 chars')
        flash('@@@@@@ PW has to be AT LEAST 3 chars!','register')
        errorValidation = True
    if request.form['password'] != request.form['confirm_password']:
        print('@@@@@@@ PW DO NOT MATCH!!! - DO NOT REGISTER user')
        flash('Pws do not match!', 'register')
        errorValidation = True

    print('!!!!! ARE THERE ERRORS IN THE REGISTATION ? = ', errorValidation)
    #========= final validation ======================
    if errorValidation == False:
        if request.form['password'] == request.form['confirm_password']:
            print('!!!! PW match!')
            # if pw match CREATE HASH
            pw_hash = bcrypt.generate_password_hash(request.form['password'])  
            print('############# pw_hash =', pw_hash)
            # now set up the obj keys and vals that will be passed into the query
            final_data = {
                'name': request.form['name'],
                'email': request.form['email'],
                'password_hash': pw_hash,
                'created_at': '',
                'updated_at': '' 
            }
            # write pass the query !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            final_query = "INSERT INTO users (name, email, password, created_at, updated_at) VALUES (%(name)s, %(email)s, %(password_hash)s, NOW(), NOW());"
            # now pass it to the db and execute it
            result = mysql.query_db(final_query, final_data)
            print('@@@@@@@@@@@@@ passed all validations @@@@@@@@')
            print('this is result = ', result) # !!!!! this gives the id!!!!
            print('@@@@@@@@@@@@@ should be redirected to /wall')
            # set id of the user so to be used in check inside wall redirect
            session['id'] = result
            session['name'] = request.form['name']
            print("# # # # # # # user registered - session['id'] is now =>", session['id'])
            return redirect('/wall')
            print('#$#$#$##$#$#$#$#$#$ # #$#$ # $# #$')
    # else:
    #         flash('something happened... could not log in', 'register')
    #         print('###### if you reach this point, all validations passed BUT not the PW match :( ')
    return redirect('/')

# ================================== WALL ====================================
@app.route('/wall')
def wall():
    print('\n ================ inside /wall ================')
    if 'id' in session:
        #display messages & users by joining the tables
        # query = "SELECT * FROM messages;"
        # print(query) # just prints the about statement
        # results = mysql.query_db(query)
        # print(results) # prints the entire table with all the objects!!!!
        # print(results[0]['user_id'])

        # query to get name, content, created at JOIN 2 tables users and messages to post on the html thru a loop
        #display messages & users by joining the tables
        query_name_post = "SELECT users.id, users.name, messages.content, messages.created_at FROM users JOIN messages ON users.id = messages.user_id;"
        results = mysql.query_db(query_name_post) # returns an array of the objs requested in the query
        print(' =-=-=--=--=--=- results from name and comment JOIN', results)
        return render_template('wall.html', name=session['name'], messagesHtml=results)
    else:
        print('@@@@@@@@@ someone tried to access wall without being logged in')
        print('@@@@@@ redirecting to /')
        return redirect('/')

# ================================== POST MESSAGE ==================================
@app.route('/postmessage', methods=['post'])
def postmessage():
    print('\n ======= inside /postmessage ========')
    print('@@@@@@@@@@@@@@ this is the message the user types :\n', request.form['content'])
    data ={'user_id': session['id'], 'content': request.form['content'], 'created_at':'','updated_at':''}
    query = "INSERT INTO messages (user_id, content, created_at, updated_at) VALUES (%(user_id)s, %(content)s, NOW(), NOW());"
    result = mysql.query_db(query, data)
    return redirect('/wall')

# ================================== POST COMMENT REPLY ==================================
@app.route('/postcomment', methods=['post'])
def postcomment():
    print('\n ========== inside /post commnet REPLY ==========')
    print('@@@@@@@@ this is the reply received by the used', request.form['comment'])

    return redirect('/wall')
# ================================== LOGOUT ==================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)
