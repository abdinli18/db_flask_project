from flask import Flask, render_template, request, redirect,session,url_for
import os
from db_init import initialize
from flask_session import Session
from psycopg2 import extensions
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

from queries import*

extensions.register_type(extensions.UNICODE)
extensions.register_type(extensions.UNICODEARRAY)

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.secret_key = b'0\x81YV\xe9\xaaQ\x9c\xfc*\xf0\xf3\x0e\xc7\xa5H'

TYPES = [
    "benefactor",
    "patient"
]


DISEASES=[]

HEROKU=True

if(not HEROKU):
    os.environ['DATABASE_URL'] = "dbname='postgres' user='postgres' host='localhost' password='27022000e'"
    initialize(os.environ.get('DATABASE_URL'))

REGISTRANTS={}

class User(UserMixin):
    def __init__(self, my_id, username, password):
        self.id = my_id
        self.username = username
        self.password = password
    
    def get_id(self):
        return self.id

def get_user(my_id):
    password  = select("name, password", "my_user", "id={}".format(my_id),asDict=True)
    password_ = password['password']
    username = password['name']
    #print(username)
    #print(password_)
    #print("heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeey")
    if password:
        user = User(my_id,username, password_)
    else:
        user = None
    return user

@login_manager.user_loader
def load_user(my_id):
    return get_user(my_id)




@app.route("/",methods=["GET"])
def index():
    if not current_user.is_authenticated:
        return render_template("index.html")
    else:
        my_id = current_user.get_id()
        my_type = select("type","my_user", "id={}".format(my_id),asDict=True)
        if(my_type['type']=="patient"):
            return redirect(url_for('users'))
        else:
            return redirect(url_for('benefactor'))

###############
@app.route("/register", methods=["POST","GET"])
def display_register():
    if request.method == "GET":
        return render_template("register.html", types = TYPES)
    else:
        is_reg = request.form.get("register")
        name = request.form.get("name")
        password = request.form.get("password")
        my_type = request.form.get("type")
        my_query = insert( "my_user"," password, name, country, type", "{},'{}', 'Azerbaijan','{}'".format(password,name, my_type))
        if(my_type=="benefactor"):
            my_query = insert( "charity_person","id, donated_patients, balance", "{},{},{}".format(my_query[0][0],0,0))
        else:
            my_query = insert( "patient","id, charity_person_helped", "{},{}".format(my_query[0][0],0))
        return render_template("success.html", message = "You are registred!")

#    is_reg = request.form.get("register")
#    is_reg_again = request.form.get("back_register")
#    if is_reg:
#        return render_template("register.html", types = TYPES)
#    if is_reg_again:
#        return render_template("register.html", types = TYPES)


#@app.route("/check_register", methods=["GET"])
#def register():
#    if request.method =="GET":
#        return render_template("success.html", message = "You are registred!") 
#    #is_reg = request.form.get("register")
#    name = request.form.get("name")
#    back = request.form.get("back")

#    if back:
#        return redirect("/")
#    if not name:
#        return render_template("error.html", message = "Missing name")
#    password = request.form.get("password")
#    if not password:
#        return render_template("error.html", message = "Missing password")
#    my_type = request.form.get("type")
#    if not my_type:
#        return render_template("error.html", message = "Missing type")
#    if my_type not in TYPES:
#        return render_template("error.html", message = "Invalid type")

#    my_query = insert( "my_user"," password, name, country, type", "{},'{}', 'Azerbaijan','{}'".format(password,name, my_type))
#    #my_id=my_query
#    #print(my_id[0][0])
#    if(my_type=="benefactor"):
#        my_query = insert( "charity_person","id, donated_patients, balance", "{},{},{}".format(my_query[0][0],0,0))
#    else:
#        my_query = insert( "patient","id, charity_person_helped", "{},{}".format(my_query[0][0],0))
#    return render_template("success.html", message = "You are registred!")
##########
#@app.route("/go_to_register", methods=["POST","GET"])
#def go_to_register():
#    return render_template("register.html", types = TYPES)

@app.route("/sign_in")
def sign_in():
    return render_template("sign_in.html", types = TYPES)


@app.route("/login", methods=["POST","GET"])

def login():
    if request.method=="POST":
        register = request.form.get("register")
        is_sign_in = request.form.get("sign_in")
        if not register:
            if not is_sign_in:
                name = request.form.get("name")
                password = int(request.form.get("password"))
                is_login = request.form.get("login")
                if is_login:
                    users = select("id, password, name, type", "my_user","name='{}'".format(name), asDict=True)
                    if users != None:
                        if users['password']==password:
                            #session["name"] = name
                            user_i = get_user(users['id'])
                            login_user(user_i)
                            if(users['type']=="patient"):
                                return redirect(url_for('users'))##loginnden bura gelir patient
                            if(users['type']=="benefactor"):
                                return redirect(url_for('benefactor'))#loginnden bura gelir patient
                            #return redirect("/users")##loginnden bura gelir
                        elif users['password']!=password:
                            #print(type(password))
                            #print(type(users['password']))
                            return render_template("error.html", message="Wrong password")
                    else:
                        if users == None:
                            return render_template("error.html", message="There is not such account")
                else:
                    return redirect("/")
            else:
                return redirect("/sign_in")
        else:
            return redirect("/register")
    else:
        return render_template("sign_in.html")
#@app.route("/greet", methods=["POST"])
#def greet():
#    return render_template("greet.html", name=request.form.get("name","world"))

@app.route("/users", methods=["GET", "POST"])
def users():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method=="GET":
        my_patient_id=current_user.get_id()
        my_query = select("application_id,amount_of_help, title, application_duration, numof_charity_people, date, approved,patient_id", "application_for_charity","patient_id={}".format(my_patient_id),asDict=True)
        #print(my_query)
        return render_template("user_view_patient.html",applications=my_query)
        #burda islemler
    users = select("id, password, name, country, type", "my_user", asDict=True)
    #applications = select("id")
    return render_template("user_view.html", users=users, my_type=my_type)


@app.route("/benefactor", methods=["GET", "POST"])
def benefactor():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method=="GET":
        my_query=select("application_id,amount_of_help, title, application_duration, numof_charity_people, date, approved,patient_id", "application_for_charity","approved={}".format(True),asDict=True)
        return render_template("benefactor.html", applications=my_query)
    else:
        if "donate" in request.form:
            user_id = current_user.get_id()
            donation = int(request.form.get("amount"))
            my_balance = select("balance","charity_person", "id={}".format(user_id),asDict=True)
            check_first = select("amount_of_help,application_duration", "application_for_charity","application_id={}".format(request.form.get('donate')),asDict=True)
            if((my_balance['balance']>=donation and donation>0) and check_first['amount_of_help']<check_first['application_duration']):
                update("charity_person","balance=balance-{}".format(donation), "id={}".format(user_id))
                update("application_for_charity","amount_of_help = amount_of_help + {}, numof_charity_people = numof_charity_people+1".format(donation), "application_id={}".format(request.form.get('donate')))
                check = select("amount_of_help, application_duration","application_for_charity", "application_id={}".format(request.form.get('donate')),asDict=True)
                if(check['amount_of_help']>=check['application_duration']):
                    payback=check['amount_of_help']-check['application_duration']
                    update("application_for_charity","application_duration=-1,amount_of_help = amount_of_help-{}".format(payback), "application_id={}".format(request.form.get('donate')))
                    update("charity_person","balance=balance+{}".format(payback), "id={}".format(user_id))
                    delete("disease_application", "application_id={}".format(request.form.get('donate')))
                    delete("application_for_charity","amount_of_help>={}".format(check['application_duration']))
        return redirect(url_for('benefactor'))


@app.route("/increase_balance", methods=["GET", "POST"])
def increase_balance():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template("add_balance.html")
    else:
        added_balance = int(request.form.get("balance_amount"))
        my_id = current_user.get_id()
        if added_balance:
            update("charity_person", "balance = balance + {}".format(added_balance),"id={}".format(my_id))
        return redirect(url_for('benefactor'))


@app.route("/apply_for_donation",methods=["POST","GET"])
def apply_donation():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "GET":
        #print("heyo")
        return render_template("take_apply.html")
    else:
        if request.form.get("apply"):
            my_title = request.form.get("title")
            my_app_dura = int(request.form.get("app_dura"))
            num_of_charitable = 0
            amount_of_help=0
            my_date = int(request.form.get("date"))
            approved = True   #daha sonra deyis bunu admin elave edenden sonra
            patient_id=current_user.get_id() 
            my_query = insert( "application_for_charity","amount_of_help, title, application_duration, numof_charity_people, date, approved, patient_id", "{},'{}', {},{},{},{},{}".format(amount_of_help,my_title, my_app_dura,num_of_charitable,my_date,approved,patient_id), returnID=True)
            while(len(DISEASES)!=0):
                #print(my_query[0][0])
                disease_name = DISEASES.pop()
                disease_data=select("disease_id", "disease","disease_name='{}'".format(disease_name),asDict=True)
                if disease_data:
                    insert("disease_application", "application_id, disease_id", "{},{}".format(my_query[0][0], disease_data['disease_id']), returnID=True)
                else:
                    insert("disease", "disease_name", "'{}'".format(disease_name))
                    disease_data=select("disease_id", "disease","disease_name='{}'".format(disease_name),asDict=True)
                    #print(disease_data)
                    insert("disease_application", "application_id, disease_id", "{},{}".format(my_query[0][0], disease_data['disease_id']), returnID=True)
            return redirect(url_for('users'))
        elif request.form.get("add_disease"):
            DISEASES.append(request.form.get("disease"))
            return redirect(url_for('apply_donation'))


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    #app.run(host="127.0.0.1", port=8080, debug=True)
    if(not HEROKU):
        app.run(debug=True)
    else:
        app.run()