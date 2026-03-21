import tkinter as tk

root = tk.Tk()
root.title("Anderson & Silva (1997)")
root.minsize(800, 600)


# define variables that can be collected from user inputs
mag_var = tk.IntVar()
r_rup_var = tk.IntVar()
mechanism_var = tk.IntVar()
hanging_wall_var = tk.BooleanVar()
site_type_var = tk.BooleanVar()
motion_type_var = tk.BooleanVar()



# defining a function that will
# get the name and password and 
# print them on the screen
def submit():

    name=name_var.get()
    password=passw_var.get()

    print("The name is : " + name)
    print("The password is : " + password)

    name_var.set("")
    passw_var.set("")


# creating a label for 
# name using widget Label
mag_label = tk.Label(root, text = 'EQ Magnitude', font=('calibre',10, 'bold'))

# creating a entry for input
# name using widget Entry
mag_entry = tk.Entry(root, textvariable = mag_var, font=('calibre',10,'normal'))

# creating a label for password
passw_label = tk.Label(root, text = 'Password', font = ('calibre',10,'bold'))

# creating a entry for password
passw_entry=tk.Entry(root, font = ('calibre',10,'normal'))

# creating a button using the widget 
# Button that will call the submit function 
sub_btn=tk.Button(root,text = 'Submit', command = submit)

# placing the label and entry in
# the required position using grid
# method
name_label.grid(row=0,column=0)
name_entry.grid(row=0,column=1)
passw_label.grid(row=1,column=0)
passw_entry.grid(row=1,column=1)
sub_btn.grid(row=2,column=1)
 
# performing an infinite loop 
# for the window to display
root.mainloop()

root.mainloop()