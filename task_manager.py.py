from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
from datetime import date, datetime
import time, math
import sqlite3
import re
import os

root = Tk()

# Width and Height of root window.
window_width = 300
window_height = 150

# Calculates the x and y position for the root window to be placed center screen.
width = root.winfo_screenwidth() / 2
height = root.winfo_screenheight() /2
xPos = int(width - (window_width / 2))
yPos = int(height - (window_height / 2))

# List to hold all users details, and the users details for this session.
session = {
    "logins": 0
}

dropdown_created = False

# List which holds the users options available to them.
options = ["Register User", "Add Task", "View All Tasks", "View My Tasks", "Exit Program"]

# Files needed for management of users and tasks

# Database
# Creates a database or connects to a pre-exisiting database.
conn = sqlite3.connect('task_manager.db')

# Create cursor
c = conn.cursor()

# Creates a tasks table that stores the relevant data associated with each task
c.execute("""CREATE TABLE IF NOT EXISTS tasks(
    username text, 
    task_title text, 
    task_description text,
    assignment_date text, 
    due_date text,
    task_completed text
    )""")

# Creates a users table that stores the username and password of each registered user for later reference
c.execute("""CREATE TABLE IF NOT EXISTS users(
    username text, 
    password text
    )""")

def loadUserDetails():
    """Load users details.
    
    Create a new list to hold each users credentials.
    Open the user file and use regEx patterns to match their username and password.
    Loop through each line of the file.
    Store the username and password match for each line in a tuple for later reference.
    Append the tuple containing the users credentials to the details list.
    """
    global details
    details = []
    
    users = open("user.txt", 'r+', encoding='utf-8')
    username_regEx = re.compile(r'\b[a-zA-Z0-9]\w+,')
    password_regEx = re.compile(r',\s[a-zA-Z0-9]\w+')
    for line in users:
        username = ""
        password = ""
        user_match = username_regEx.finditer(line)
        password_match = password_regEx.finditer(line)
        for user in user_match:
            username = user.group(0)[:-1]
        for pass_word in password_match:
            password = pass_word.group(0)[2:]
        details.append((username, password))

def loadTaskDetails():
    """Load task details.
    
    Create a new list to hold all tasks.
    Open the task file and loop through each line.
    Remove the new line character from each line.
    Split the tasks into a list seperated at each comma, and append to the all tasks list.
    """
    global all_tasks
    all_tasks = []
    
    with open("tasks.txt") as tasks:
        for line_num, line in enumerate(tasks):
            line_replace = line.replace("\n", "")
            split_tasks = line_replace.split(", ")
            split_tasks.insert(0, line_num + 1)
            all_tasks.append(split_tasks) 
    
    writeTaskListToFile()

def loadUserTaskDetails():
    """Load logged in users task details.
    
    Create a new list to hold this users task.
    Loop through each task in the all tasks list.
    Check if the username associated with each task matches the username that is currently logged in.
    If there is a match, append that particular tast to the this users tasks list.
    """
    global this_users_tasks 
    this_users_tasks = []
   
    loadTaskDetails()    
    for index in range(0, len(all_tasks)):
        if all_tasks[index][1] == session["username"]:
            this_users_tasks.append(all_tasks[index])
            
def countAllTasks():
    """Count all tasks and return list.
    
    Create a new list to hold the task numbers.
    Loop through each line in the task file.
    Use a counter to track the number of each line.
    Append the number of each line to the task range list.
    Return the list in order for it to be used by the user for task selection.
    """
    task_range = []
    counter = 1
    with open("tasks.txt") as tasks:
        for line in tasks:
            task_range.append(counter)
            counter +=1
    return task_range

def countUserTasks():
    """Count logged in users task and return list.
    
    Create a new list to hold this users task numbers.
    Loop through each task in the all tasks list.
    Check if the username associated with each task, matches the username that is currently logged in.
    If there is a match, use a counter to track the number of each task.
    Append the number of each task to a list.
    Return the list in order for it to be used by the user to select their own tasks. 
    """
    user_task_range = []
    counter = 1
    for index in range(0, len(all_tasks)):
        if all_tasks[index][1] == session["username"]:
            user_task_range.append(counter)
            counter +=1
    return user_task_range

def checkUserExists(username_to_check):
    """Check if the username passed is in the username list."""
    for username in details:
        if username[0] == username_to_check:
            return True
    return False
    
def createDropdown():   
    """Create a dropdown window.
    
    Create a dropdown menu and pass in the options lists.
    The options represent the choices the program enables the user.
    Create a submittion button to call on an external function to handle the users option.
    """
    option = StringVar()
    option.set(options[0])
    
    if session["username"] == "admin":
        options.insert(-1, "Generate Reports")
        options.insert(-1, "Task Statistics")
        
        
    global dropdown_menu
    dropdown_menu = newWindow(400, 100, "Dropdown Menu")
    dropdown_menu.protocol("WM_DELETE_WINDOW",lambda: logout(dropdown_menu))
    
    drop = OptionMenu(dropdown_menu, option, *options)
    drop.pack(pady=15, ipadx=30)
    
    btn = Button(dropdown_menu, text="Confirm Selection", command=lambda: userSelection(option))
    btn.pack()

def createRegisterWindow():
    """Create the register window for the user"""
 
    register_window = newWindow(300, 150, "Register User")
    loginRegisterWindow(register_window)
   
def createTaskWindow():
    """Create the task window for the user to submit tasks."""
    
    task_window = newWindow(400, 380, "Task Menu")
    newForm(task_window, "normal", 0, "All")

def createTaskSelectorWindow(user_choice):
    """Create the dropdown for the user to select a specific task.
    
    Check if the user is viewing all tasks or only their own tasks.
    Depending on the choice return the list with the number of tasks they require.
    Use that list as the options for the dropdown menu.
    Pass the task number and selection type to an external function upon user submittion.
    """
    if user_choice == "View My Tasks":
        task_range = countUserTasks()
        selection_type = "Individual"
    else:
        task_range = countAllTasks()
        selection_type = "All"
        
    task_number = IntVar()
    task_number.set(1)
    choice = newWindow(150, 120, "Select Task")
    drop = OptionMenu(choice, task_number, *task_range)
    btn = Button(choice, text="Select Task", command=lambda: newForm("none", "readonly", task_number, selection_type))
    drop.pack(pady=20)
    btn.pack()    
    
def createTaskStatisticWindow():
    """Create the task statistic window.
    
    Display the number of tasks and users by retrieving the length of their lists.
    """
    stats_window = newWindow(200, 110, "Task Statistics")
    
    Label(stats_window, text=f"Number of Tasks: {len(all_tasks)}").pack(pady=15)
    Label(stats_window, text=f"Number of users: {len(details)}").pack()

def createTaskOverview():
    """Calculate task statistics and write to file.
    
    Loop through all the tasks stored in the all task list.
    Look at the correct index to determine whether the task has been completed.
    Use counters to keep track of the completed and uncompleted tasks.
    Calculate if the task is overdue using the date timestamps.
    Calculate the percentage based on the information retrieved.
    Write the details to a file.
    Call the report screen function to show this information the user.
    """
    completed, incompleted, overdue = 0, 0, 0
    total_tasks = len(all_tasks)
    for task in all_tasks:
        if task[-1] == "Yes":
            completed += 1
        else: 
            incompleted += 1
            due_date = datetime.strptime(task[5], "%Y-%m-%d").timestamp()
            today = time.time()
            if today > due_date:
                overdue += 1
    task_percentage = 100 / total_tasks
    percentage_incomplete = math.trunc(task_percentage * incompleted)
    percentage_overdue = math.trunc(100 / incompleted * overdue )
    
    with open("task_overview.txt", "a") as tasks:
        tasks.seek(0)
        tasks.truncate()
        tasks.write(f"Total Number of Tasks: {total_tasks}\n")
        tasks.write(f"Completed Tasks: {completed}\n")
        tasks.write(f"Incomplete Tasks: {incompleted}\n")
        tasks.write(f"Overdue Tasks: {overdue}\n")
        tasks.write(f"Tasks Incomplete: {percentage_incomplete}%\n")
        tasks.write(f"Tasks Overdue: {percentage_overdue}%")

    showReportScreen("tasks")

def createUserOverview(username, choice):
    """Calculate User Statistics and write to file."""
    
    #Retrieve the username as a parameter and create a list of that users task.
    this_users_tasks = []
    for task in all_tasks:
        if task[1] == username.get():
            this_users_tasks.append(task)
    
    #If the user has no tasks display a warning to the user.
    if len(this_users_tasks) == 0:
        if messagebox.showwarning(title="No Tasks Available", message=f"{username.get()} has not submitted any tasks."):
            choice.lift()
    else:
        #If the user has tasks, create the necessary variables to store their statistics.
        completed, incompleted, overdue = 0, 0, 0 
        
        #Get the length of the lists that hold the users and tasks details.
        num_users, user_tasks, total_tasks = len(details), len(this_users_tasks), len(all_tasks) 
        
        #Loop through the users tasks and look at the correct index to determine task completion.
        #Calculate if the task is overdue using the date timestamps. 
        for task in this_users_tasks:
            if task[-1] == "Yes":
                completed += 1
            else:
                incompleted += 1
                due_date = datetime.strptime(task[5], "%Y-%m-%d").timestamp()
                today = time.time()
                if today > due_date:
                    overdue += 1
        
        #Calculate the percentage based on the information retrieved.
        total_task_percentage = 100 / total_tasks
        user_tasks_percentage = 100 / user_tasks
        user_task_percentage = math.trunc(total_task_percentage * user_tasks)

        if completed > 0:
            percentage_complete = math.trunc(user_tasks_percentage * completed)
        else:
            percentage_complete = 0
        
        if incompleted > 0:
            percentage_incomplete = math.trunc(user_tasks_percentage * incompleted)
        else:
            percentage_incomplete = 0
        
        if overdue > 0:
            percentage_overdue = math.trunc(100 / incompleted * overdue ) 
        else:
            percentage_overdue = 0
        
        #Write the information to the user overview file.
        with open("user_overview.txt", "a") as users:
            users.seek(0)
            users.truncate()
            users.write(f"Username of User: {username.get()}\n")
            users.write(f"Total Number of Users: {num_users}\n")
            users.write(f"Total Number of Tasks: {total_tasks}\n")
            users.write(f"Total Number of Users Tasks: {user_tasks}\n")
            users.write(f"Tasks Assigned to User: {user_task_percentage}%\n")
            users.write(f"Users Tasks Completed: {percentage_complete}%\n")
            users.write(f"Users Tasks Incomplete: {percentage_incomplete}%\n")
            users.write(f"Users Tasks Overdue: {percentage_overdue}%")
        
        #Call the report screen function to show this information the user.
        showReportScreen("users")        
    
def checkDetails(user_to_check, password_to_check):
    """Check users details to determine their existence.
        
    Loop through the user details list.
    Search the list for the username and password passed into the function.
    If both the username and password are correct return true, otherwise return false.
    """
    for username, password in details:
        if username == user_to_check and password == password_to_check:
            return True
            break
        elif username == user_to_check: 
            print("Your password is incorrect")
            break
        elif password == password_to_check: 
            print("Your username is incorrect")
            break
            
    return False    

def completeCheckPressed(task_completion, task_num, selection_type): 
    """Task Completed Check.
    
    Receive the state of the completed button located on the edit task form.
    Using the task number find the task being edited in the all tasks list.
    Depending on the state change the task completion to Yes or No.
    Update the information on the form.
    Write the new changes to the task file.
    """
    if selection_type == "All":
        if checkButtonVar.get() == 1:
            all_tasks[task_num.get() -1][-1] = "Yes"
        else:
            all_tasks[task_num.get() -1][-1] = "No"
        task_completion.config(state="normal")
        task_completion.delete(0, END)
        task_completion.insert(0, all_tasks[task_num.get() -1][-1])
        task_completion.config(state="disabled")
    else:
        list_id = this_users_tasks[task_num.get() -1][0]
        if checkButtonVar.get() == 1:
            all_tasks[list_id - 1][-1] = "Yes"
        else:
            all_tasks[list_id - 1][-1] = "No"
        task_completion.config(state="normal")
        task_completion.delete(0, END)
        task_completion.insert(0, all_tasks[list_id - 1][-1])
        task_completion.config(state="disabled")
    writeTaskListToFile()

def editTask(container, username, title, description, assign_date, due_date, task_completion, task_num, selection_type):
    """Change the state of the form for editting.
    
    Depening on the button state disable or enable the entry boxes for editting.
    If the user is submitting a revised entry double check he wishes to continue.
    If so, call the update task function and pass the entry boxes as parameters.
    """
    if btn_text.get() == "Edit Task":
    
        username.config(state="normal")
        title.config(state="normal")
        description.config(state="normal")
        due_date.config(state="normal")
        task_completion.config(state="normal")
        btn_text.set("Submit Revisions")
        
    else:
        if messagebox.askokcancel(title="Revisions", message="Are you sure you wish to continue with these revisions?"):
            container.lift()
            
            btn_text.set("Edit Task")
           
            username.config(state="disable")
            title.config(state="disable")
            description.config(state="disable")
            due_date.config(state="disable")
            task_completion.config(state="disable")
            
            updateTask(username, title, description, due_date, assign_date, task_completion, task_num, selection_type)

def updateTask(username, title, description, due_date, assign_date, task_completion, task_num, selection_type):
    """Update Task in List
    
    Receieve the task number and the entry box text.
    Use the task number to retrieve the correct task.
    Update the information associated with the task in the list.
    Call the function that updated the task list to the file.
    """
    
    task_number = task_num.get() -1
    if selection_type == "Individual":
        task_number = this_users_tasks[task_number][0] - 1
    all_tasks[task_number][1] = username.get()
    all_tasks[task_number][2] = title.get()
    description = description.get(1.0, END).rstrip('[\n\t]')
    all_tasks[task_number][3] = description
    all_tasks[task_number][5] = due_date.get()
    all_tasks[task_number][6] = task_completion.get()
    writeTaskListToFile()
   
def viewTaskDetails(username, title, description, assign_date, due_date, task_completion, task_number, selection_type):
    """Retrieve the relevant task information and display to the user.
    
    Depending on the selection type retrieve the task from this users tasks or all tasks.
    Insert the task information into an entry box and disable the box to read only.
    """
    task_number = int(task_number.get()) - 1
    if selection_type == "All":
        username.insert(0, all_tasks[task_number][1])
        title.insert(0, all_tasks[task_number][2])
        description.insert(1.0, all_tasks[task_number][3])
        assign_date.insert(0, all_tasks[task_number][4])
        due_date.insert(0, all_tasks[task_number][5])
        task_completion.insert(0, all_tasks[task_number][6])
    else:
        username.insert(0, this_users_tasks[task_number][1])
        title.insert(0, this_users_tasks[task_number][2])
        description.insert(1.0, this_users_tasks[task_number][3])
        assign_date.insert(0, this_users_tasks[task_number][4])
        due_date.insert(0, this_users_tasks[task_number][5])
        list_id = this_users_tasks[task_number][0] - 1
        task_completion.insert(0, all_tasks[list_id][6])
    
    username.config(state="disabled", disabledbackground="white", disabledforeground="black")
    title.config(state="disabled", disabledbackground="white", disabledforeground="black")
    description.config(state=DISABLED)
    assign_date.config(state="disabled", disabledbackground="white", disabledforeground="black")
    due_date.config(state="disabled", disabledbackground="white", disabledforeground="black")
    task_completion.config(state="disabled", disabledbackground="white", disabledforeground="black")

def loginUser(username, password):
    """Log In User and add their username to the session dictionary."""
    
    if checkDetails(username.get(), password.get()):
        session["username"] = username.get()
        session["logins"] += 1
        createDropdown()
    username.delete(0, END)
    password.delete(0, END)

def loginRegisterWindow(container):
    """Create the window for the user to either log in or register.
    
    Create the form.
    Depening on the container create a submittion button to login or register.
    When the submittion button is pressed call on the relevant function.
    Pass the username and password entered into the function. 
    """
    frame = Frame(container)
    frame.grid(padx=20, pady=20)
        
    Label(frame, text="Username:").grid(row=0)
    Label(frame, text="Password:").grid(row=1)

    username = Entry(frame, width=30)
    username.grid(row=0, column=1, padx=5, pady=10)
    password = Entry(frame, width=30)
    password.grid(row=1, column=1, padx=5)
    
    if container == root:
        submit_btn = Button(container, text="Login", command=lambda: loginUser(username, password)).grid(row=2, column=0, columnspan=2, padx=10, ipadx=120)
    else:
        submit_btn = Button(container, text="Register", command=lambda: registerUser(username, password, container)).grid(row=2, column=0, columnspan=2, padx=10, ipadx=100)

def userSelection(option):
    """Receive the users menu option and call the necessary function"""
    
    user_choice = option.get()
    
    if user_choice == "Exit Program":
        root.destroy()
    
    if user_choice == "Register User" and session["username"] == "admin":
        createRegisterWindow()
    elif user_choice == "Register User" and session["username"] != "admin":
        if messagebox.showwarning("Insufficient Privillages", "Sorry, only admin can register users."):
            dropdown_menu.lift()
        
    if user_choice == "Add Task":
        loadTaskDetails()
        createTaskWindow()
    
    if user_choice == "View All Tasks": 
        loadTaskDetails()
        if len(all_tasks) > 0:   
            createTaskSelectorWindow(user_choice)
        else:
            if messagebox.showwarning("No Posts Available", "There are no current posts in the task manager."):
                dropdown_menu.lift()
                
    if user_choice == "View My Tasks":
        loadUserTaskDetails()
        if len(this_users_tasks) > 0:
            createTaskSelectorWindow(user_choice)
        else:
            if messagebox.showwarning("No Posts Available", "There are no current posts belonging to this user."):
                dropdown_menu.lift()
    
    if user_choice == "Task Statistics":
        loadTaskDetails()
        loadUserDetails()
        createTaskStatisticWindow()
    
    if user_choice == "Generate Reports":
        loadTaskDetails()
        loadUserDetails()
        loadUserTaskDetails()
        reportSelection()

def reportSelection():
    username, usernames = StringVar(), []
    for user in details:
        usernames.append(user[0])
        
    username.set(usernames[0])
    choice = newWindow(150, 180, "Select Username")
    drop = OptionMenu(choice, username, *usernames)
    task_btn = Button(choice, text="Get Task Report", command=createTaskOverview)
    user_btn = Button(choice, text="Get User Report", command=lambda: createUserOverview(username, choice))
    task_btn.pack(pady=30)
    drop.pack()
    user_btn.pack(pady=10)
    
def registerUser(username, password, window):
    """Submit new user.
    
    Open the user file.
    Check if the file already holds text.
    If their is text append the task to a new line, if not write the task to the first line.
    Destroy the register window after submittion.
    """
    if checkUserExists(username.get()):
        messagebox.showwarning("Username exists", "Sorry, username already exists, enter another.")
        window.lift()
    else: 
        with open("user.txt", "a") as users:
            if(os.path.getsize("user.txt") > 0):
                users.write(f"\n{username.get()}, {password.get()}")
            else:
                users.write(f"{username.get()}, {password.get()}")
        if messagebox.showinfo("Registration Successful", "Successfully registered, you can now log in."):
            dropdown_menu.lift()
                
def submitTask(username, title, description, assignment_date,  due_date, task_completion):
    """Submit user task.
    
    Open the task file.
    Check if the file already holds text.
    If their is text append the task to a new line, if not write the task to the first line.
    Delete the contents of the the task form after writing is complete.
    """
    with open("tasks.txt", "a") as tasks:
        tasks.write(f"{username.get()}, {title.get()}, {description.get()}, {assignment_date}, {due_date.get()}, {task_completion.get()}\n")
        
    username.delete(0, END)
    title.delete(0, END)
    description.delete(0, END)
    due_date.delete(0, END)

def showReportScreen(report_type):
    
    if report_type == "tasks":
        report_screen = newWindow(250, 300, "Report")
        Label(report_screen, text="").grid(row=0)
        with open("task_overview.txt", "r") as overview:
            title_regEx = re.compile(r'[\s\w+]*:')
            data_regEx = re.compile(r'\d+(%)?')
            for line_num, text in enumerate(overview):
                title_match = title_regEx.finditer(text)
                data_match = data_regEx.finditer(text)
                for title in title_match:
                    title = title.group(0)
                    Label(report_screen, text=title).grid(row=line_num + 1, column=0,padx=25, pady=10, sticky=E)
                for data in data_match:
                    data = data.group(0)
                    entry = Entry(report_screen, width=5)
                    entry.grid(row=line_num + 1, column=1, pady=10)
                    entry.insert(0, data)
    else:
        report_screen = newWindow(295, 280, "Report")
        Label(report_screen, text="").grid(row=0)
        with open("user_overview.txt", "r") as overview:
            title_regEx = re.compile(r'[\s\w+]*:')
            data_regEx = re.compile(r'\d+(%)?')
            for line_num, text in enumerate(overview):
                title_match = title_regEx.finditer(text)
                data_match = data_regEx.finditer(text)
                if line_num > 1:
                    for title in title_match:
                        title = title.group(0)
                        Label(report_screen, text=title).grid(row=line_num + 1, column=0,padx=25, pady=10, sticky=E)
                    for data in data_match:
                        data = data.group(0)
                        entry = Entry(report_screen, width=5)
                        entry.grid(row=line_num + 1, column=1, pady=10)
                        entry.insert(0, data)
               
def newWindow(window_width, window_height, window_title):
    """Create a new top level window and return"""
    
    global width, height
    
    xPos = int(width - (window_width / 2))
    yPos = int(height - (window_height / 2))

    top = Toplevel()
    top.geometry(f"{window_width}x{window_height}+{xPos}+{yPos}")
    
    return top
    
def newForm(container, view_mode, task_num, selection_type):
    """Create the form for the user to either add a new task or view a task.
    
    If the view_mode is read only,
    complete the form layout as normal but call the viewTaskDetails function.
    If view_mode is not read only then allow task submittion.
    """
    def liftDropdown():
        container.destroy()
        dropdown_menu.lift()
    
    if view_mode == "readonly":
        container = newWindow(400, 430, "View Tasks")
        
    frame = Frame(container)
    frame.grid(padx=55)
    
    container.protocol("WM_DELETE_WINDOW", liftDropdown)
    
    options = ["No", "Yes"]
    global task_option
    task_option = StringVar()
    task_option.set(options[0])
    
    Label(container, text="").grid(row=0)
    Label(container, text="Task Number").grid(row=1)
    Label(container, text="Username:").grid(row=2, padx=30)
    Label(container, text="Title:").grid(row=3)
    Label(container, text="Description:").grid(row=4)
    Label(container, text="Assignment Date:").grid(row=5)
    Label(container, text="Due Date:").grid(row=6)
    Label(container, text="Task Completed:").grid(row=7)
    
    task_number = Entry(container, width=4)
    username = Entry(container, width=40)
    title = Entry(container, width=40)
    
    # Allows description entry if view mode is not read only
    if view_mode == "readonly":
        global checkButtonVar
        checkButtonVar = IntVar()
        description = Text(container, width=30, height=5)
        task_completion = Entry(container, width=40)
        Checkbutton(container, text="Completed", variable=checkButtonVar, command=lambda: completeCheckPressed(task_completion, task_num, selection_type)).grid(row=1, column=1, sticky=E)
        if selection_type == "Individual":
            list_id = this_users_tasks[task_num.get() - 1][0] - 1
            task_number.insert(0, f"{all_tasks[list_id][0]}")
        else:
            task_number.insert(0, f"{task_num.get()}")
    else:
        description = Entry(container, width=40)
        task_completion = OptionMenu(container, task_option, *options)
        task_number.insert(0, f"{len(all_tasks) + 1}")
        
    due_date = Entry(container, width=40)
    assignment_date = date.today()
 
    assign_date = Entry(container, width=40)
    assign_date.insert(0, assignment_date)
    task_number.config(state="disabled", disabledbackground="grey", disabledforeground="black")
    assign_date.config(state="disabled", disabledbackground="white", disabledforeground="black")

    entry_padding=10
    task_number.grid(row=1, column=1, pady=entry_padding, sticky=W)
    username.grid(row=2, column=1, pady=entry_padding)
    title.grid(row=3, column=1, pady=entry_padding)
    description.grid(row=4, column=1, pady=entry_padding)
    assign_date.grid(row=5,column=1, pady=entry_padding)
    due_date.grid(row=6, column=1, pady=entry_padding)
    task_completion.grid(row=7, column=1, pady=entry_padding, sticky=W)
      
    # Calls view task details if user is readonly.
    if view_mode == "readonly":
        global btn_text, edit_btn
        btn_text = StringVar()
        btn_text.set("Edit Task")
        viewTaskDetails(username, title, description, assign_date, due_date, task_completion, task_num, selection_type)
        edit_btn = Button(container, width = 30, textvariable=btn_text, command=lambda: editTask(container, username, title, description, assign_date, due_date, task_completion, task_num, selection_type)).grid(row=8, column=1, pady=15)
    # Allows submittion of task is user is adding a task.
    else:
        btn = Button(container, width=30, text="Submit Task", command=lambda: submitTask(username, title, description, assignment_date, due_date, task_option))
        btn.grid(row=8, column=1, pady=15)   

def writeTaskListToFile():
    """Write Tasks from list the file.
    
    Open the tasks file that holds all the tasks.
    Go the beginning of the file, and remove it's contents.
    Loop through the task list, and update the task file.
    """
    with open("tasks.txt", "a") as tasks:
        tasks.seek(0)
        tasks.truncate()
        for task in all_tasks:
            tasks.write(f"{task[1]}, {task[2]}, {task[3]}, {task[4]}, {task[5]}, {task[6]}\n")
           
def logout(dropdown_menu):
    """Display a message box for when the user closes the selection menu.
    
    Ask the user if they would like to logout.
    If so then reset the options menu and destroy the selection screen.
    """
    global options
    if messagebox.askokcancel("Quit", "Do you want to logout?"):
        loadUserDetails()
        options = ["Register User", "Add Task", "View All Tasks", "View My Tasks", "Exit Program"]
        dropdown_menu.destroy()
    else:
        dropdown_menu.lift()

def onClosing():
    """Display a message box for when the user closes the root window.
    
    Ask the user if they would like to quit.
    If so destroy the root screen and exit the program.
    """
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

# Calls the functions which updates the user and task details into lists.
loadUserDetails()
loadTaskDetails()

# Set the title and geometry of the root window
root.title("Task Manager")
root.geometry(f"{window_width}x{window_height}+{xPos}+{yPos}")

# Create an event handler for when the root window close button is pressed.
root.protocol("WM_DELETE_WINDOW", onClosing)
loginRegisterWindow(root)

#Commit changes to the database.
conn.commit()

# Close the connection to the database.
conn.close()

mainloop()
