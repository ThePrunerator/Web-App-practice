from flask import Flask, render_template, request
from time import sleep
app = Flask(__name__)

#Code for the login page.
@app.route("/")
def index():
    return render_template("index.html")

#Code for authentication page.
@app.route("/authentication", methods = ["POST"])
def authentication():
    #Extracts login data from text file.
    with open('users.csv', 'r') as f:
        user_list = f.read()
        user_list = user_list.split("\n")

    #Checks for the presence of login credentials within the login data.
    username = request.form.get("username")
    password = request.form.get("password")

    for user in user_list:
        if user != None and username in user and password in user:
            f = open("curr_user.txt", "w")
            f.write(username)
            f.close()
            return get_home(user)

    return render_template("failure.html")

#Code for the home page.
def get_home(details):
    user = details.split(",")
    name = user[0]
    username = user[1]
    tests = user[3:]    #In the format <test>_<level>.
    contents = []    #Contains a list of all tests and grades that students scored in their respective subjects.

    for test in tests:
        test2 = " ".join(test.split("_")[::-1])
        data = [test2]

        with open(f"{username}_{test}.csv", "r") as f:
            lines = f.read().split("\n")

            for line in lines:
                line = line.split(",")

                if len(line) == 2:
                    data.append(line)

            contents.append(data)

    return render_template("home.html", name = name, contents = contents)

#Code for the failure page.
@app.route("/failure")
def failure():
    return render_template("failure.html")

#Code for page to register new users.
@app.route("/register")
def register():
    return render_template("register.html")

#Code to check for the new registrant's details.
@app.route("/checkregister", methods = ["POST"])
def checkregister():
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")

    with open("users.csv", "r") as f:
        user_txt = f.read()

    if " " in username or " " in password:
        error = 'Username and password cannot contain spacing between them.'
        return render_template("registerfailure.html", error = error)

    elif name in user_txt:
        error = "The name has been taken."
        return render_template("registerfailure.html", error = error)

    elif username in user_txt:
        error = "The username has been taken."
        return render_template("registerfailure.html", error = error)

    elif password in user_txt:
        error = "The password has been taken."
        return render_template("registerfailure.html", error = error)

    else:
        with open('users.csv', "a") as f:
            f.write("{},{},{}\n".format(name, username, password))

        return render_template("registersuccess.html", name = name, username = username, password = password)

#Code to add / change subjects to the user's saved data, as well as the user's grades for the subject for all exams.
@app.route("/addsubjects", methods = ["POST"])
def addsubjects():
    username = open("curr_user.txt", "r").read()
    h_level = request.form.get("H level")
    subject = request.form.get("subject")
    subject = f"{h_level} {subject}"
    grade = request.form.get("grade")
    year = request.form.get("year")
    test = request.form.get("test")
    mode = "a"

    #Checks for input format of the subject name.
    if "H1 " not in subject and "H2 " not in subject and "H3 " not in subject:
        err = "Please enter H1 / H2 / H3 subject."
        return render_template('error.html', err = err)

    #Checks for the validity of the level, as well as the level in which the student is currently in.
    if year == "1":
        level = "JC1"
    elif year == "2":
        level = "JC2"
    else:
        err = "The level has been input wrongly. Please only input either '1' or '2'."
        return render_template('error.html', err = err)

    #Assigns the test in the formatted name system.
    test = f"{test}_{level}"

    #Adds the test name into the main file, 'users.csv'.
    with open("users.csv", "r") as f:
        data = f.read().split('\n')
        index = -1
        for line in data:
            index += 1

            #If the test has not yet been added into the file,
            #create a new CSV file to store data for new test.
            if username in line and test not in line:
                data[index] += f",{test}"
                mode = "w"
        data = "\n".join(data)

    #Updates the contents.
    with open("users.csv", "w") as f:
        f.write(data)

    #Adds the test results alongside existing test results for the same exam.
    with open(f"{username}_{test}.csv", mode) as f:
        f.write(f"{subject},{grade}\n")

    #Returns the user to where they started.
    with open("users.csv", "r") as f:
        users = f.read().split('\n')

        for line in users:
            if username in line:
                return get_home(line)

    return render_template("error.html", err = "User cannot be found. Please proceed to the login page.")