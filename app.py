from flask import Flask,request,jsonify,g
from werkzeug.security import generate_password_hash , check_password_hash
import os
from access_file import open_file,update_file
import random
import string
import sqlite3
app=Flask(__name__)
app.config["DEBUG"]=True
def connect_db():
    sql = sqlite3.connect(r'pro.db')
    sql.row_factory = sqlite3.Row
    return sql
def get_db():
    if not hasattr(g,'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()

@app.route("/register",methods=["POST"])
def register():
    reg_det=request.get_json()
    req_k=["username","password","re_password","email","area","district","phone_no","income","farm_area"]
    errors=[]
    #checking for any missing keys or none values
    for k in req_k:
        try:
            reg_det[k] #would give an error if no key exists
            if reg_det[k]==None:
                r="incomplete "+k
                #appends error message to error list
                errors.append(r)
        except:
            #if error occurs this gets activated
            r="incomplete "+k
            #appends error message to error list
            errors.append(r)
    for k in reg_det.keys():
        if k not in req_k:
            r="unexpected key "+k
            errors.append(r)
    #if there is atleast an error from above process we return the errors in place of result
    if len(errors)>0:
        return jsonify({"result":errors})

    #extracting the information from input json file
    username=reg_det["username"]
    password=reg_det["password"]
    re_password=reg_det["re_password"]
    email=reg_det["email"]
    f_area=reg_det["farm_area"]
    income=reg_det["income"]
    area=reg_det["area"]
    district=reg_det["district"]
    phone_no=reg_det["phone_no"]

    #checking if password == re_password
    if password != re_password:
        msg={"result":"wrong password"}
        return jsonify(msg)

    #ENCODING PASSWORD INTO A SECURE FORMAT (USE THIS TO INSERT INTO TABLE)
    en_password=generate_password_hash(password,method="sha256")
    print("password = {}".format(en_password))

    #GENERATING FARMER ID
    number=open_file()
    r = ''.join([random.choice(string.ascii_uppercase) for n in range(10)])
    farmer_id= r+"_"+str(number)
    update_file()

    print(farmer_id)
    db=get_db()
    cur = db.execute("select district_id from district where district_name = ?",(district,))
    d_id = cur.fetchone()
    cur = db.execute("select area_id from area where area_name = ? and district_id = ?",(area,d_id['district_id'],))
    a_id = cur.fetchone()
    db.execute('insert into farmer_details (farmer_id,farmer_name,income,farm_area,area_id,password) VALUES(?,?,?,?,?,?)',(farmer_id,username,income,f_area,a_id['area_id'],en_password))
    db.execute('insert into farm_em (farmer_id , email) values(?,?)',(farmer_id , email))
    db.execute('insert into farm_num (farmer_id , mobile_no) values(?,?)',(farmer_id , phone_no))
    db.commit()
    '''

            WRITE SQL CODE TO INSERT INTO LOGIN , FARMER DETAILS TABLE TABLE

    '''

    #if no errors , result = success is returned
    msg={"result":"successs"}
    return jsonify(msg)


@app.route("/login",methods=["POST"])
def login():
    req_k=["username","password"]
    errors=[]
    log_det=request.get_json()
    #checking for any missing keys or none values
    for k in req_k:
        try:
            log_det[k] #would give an error if no key exists
            if log_det[k]==None:
                r="incomplete "+k
                #appends error message to error list
                errors.append(r)
        except:
            #if error occurs this gets activated
            r="incomplete "+k
            #appends error message to error list
            errors.append(r)
    #checking if we have recieved any unexpected keys(data)
    for k in log_det.keys():
        if k not in req_k:
            r="unexpected key "+k
            errors.append(r)
    #if there is atleast an error from above process we return the errors in place of result
    if len(errors)>0:
        return jsonify({"result":errors})

    username=log_det["username"]
    password=log_det["password"]
    db=get_db()
    cur = db.execute("select password from farmer_details where farmer_id = ?",(username,))
    pwd = cur.fetchone()
    if pwd is None:
        return jsonify({"result":"user doesnt exist"})


    '''

            WRITE SQL CODE TO GET LOGIN  DETAILS FOR THE ENTERED USERNAME FROM LOGIN TABLE

    '''
    if check_password_hash(pwd["password"],password) :
        return jsonify({"result":"logged in"})
    else:
        return jsonify({"result":"wrong password"})
if __name__=="__main__":
    app.run()
