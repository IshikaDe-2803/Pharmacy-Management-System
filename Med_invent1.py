import datetime #datetime module --> to check validity of date
from tabulate import tabulate #tabulate module--> display table in proper format
import mysql.connector #connecting mysql with python

mydb = mysql.connector.connect( #establishing connection with MySQL database
  host="localhost",
  user="root",
  password="Rootpass123*",
  database="medical_inventory",
)
mycursor = mydb.cursor() #creating mycursor object to access database elements

#class med defines the medical inventory
class med:
    def __init__(medi, ref_no,comp_name,med_type,m_name,m_qnt,m_cost): #__init__ initializes class variables
        medi.ref_no=ref_no
        medi.comp_name=comp_name
        medi.med_type=med_type
        medi.m_name=m_name
        medi.m_qnt=m_qnt
        medi.m_cost=m_cost

    #add() inserts medicinal records into the inventory
    def add(medi):
        #insertion of values into the inventory
        ins_medin = "INSERT INTO med_inv (ref_no,comp_name,med_type,m_name,m_qnt,m_cost) VALUES (%s,%s,%s,%s,%s,%s)"
        val_medin= (medi.ref_no,medi.comp_name,medi.med_type,medi.m_name,medi.m_qnt,medi.m_cost)
        mycursor.execute(ins_medin,val_medin)#executes the MySQL commands
        mydb.commit()#sends a COMMIT statement to the MySQL server, committing the current transaction
        print("\nMedicine record successfully inserted.")

#class bills defines the generation of bill section
class bills:
    def __init__(c, cust_name,cust_contact,cust_date,cust_address,cust_docref):#__init__ initializes class variables
        c.cust_name=cust_name
        c.cust_contact=cust_contact
        c.cust_date=cust_date
        c.cust_address=cust_address
        c.cust_docref=cust_docref

    def bill_ch(c):#bill_ch() takes user-choice to add/delete bill records/generate a bill
        print("\n1.Add medicine to cart\n2.Delete medicine from cart\n3.Generate bill\n")
        ch2=int(input("Enter choice: "))
        if(ch2==1):
            c.add_b()#Add medicine to bill
            print("\nMedicine successfully added.")
            c.bill_ch()
        elif(ch2==2):
            del_b()#delete medicine from bill
            c.bill_ch()
        elif(ch2==3):
            c.disp_b()#display the bill
            mainpg()
        else:
            print("\nInvalid choice.")
            c.bill_ch()

    def add_b(c):#add a medicinal record in the bill
        check=True
        while(check==True):
            m_n=input("Enter the medicine name- ")
            mycursor.execute("SELECT m_name from med_inv where m_name=%s",(m_n,))
            myresult3=mycursor.fetchone()
            mycursor.execute("SELECT m_qnt from med_inv where m_name=%s",(m_n,))
            quant=mycursor.fetchone()
            m_q=int(input("Enter the medicine quantity- "))
            if(not myresult3 or quant[0]==0):
                print("Medicine entered is not available.")
                check=True
            elif(m_q>quant[0]):
                print("Insufficient medicines in inventory. Medicine not available.")
                check=True
            else:
                check=False
        mycursor.execute("SELECT m_cost from med_inv where m_name=%s",(m_n,))
        m_cst=mycursor.fetchone()#fetching the cost of medicine
        #update inventory-quantity of medicine
        mycursor.execute("UPDATE med_inv set m_qnt=m_qnt-%s where m_name=%s",(m_q,m_n,))
        ins_bil = "INSERT INTO bill (cust_date,cust_contact,med_name,med_qnt,med_cost,med_total) VALUES (%s,%s,%s,%s,%s,%s)"
        val_bil= (c.cust_date,c.cust_contact,m_n,m_q,m_cst[0],m_cst[0]*m_q)
        mycursor.execute(ins_bil,val_bil)
        mydb.commit()
        print("Customer record added.")

    def disp_b(c):#displaying the bill
        #displaying customer details
        print("Customer Name: ", c.cust_name)
        print("Customer Contact: ", c.cust_contact)
        print("Date of purchase: ",c.cust_date)
        print("Customer Address: ", c.cust_address)
        print("Doctor referral: ", c.cust_docref)
        mycursor.execute("SELECT med_name,med_qnt,med_cost,med_total FROM bill where cust_contact=%s and cust_date=%s",(c.cust_contact,c.cust_date,))
        myresult1 = mycursor.fetchall() #Displaying  bill details
        print(tabulate(myresult1,headers = ["Medicine Name","Quantity","Cost per item","Total Cost"], tablefmt='psql',numalign="left"))
        ins_cust= "SELECT SUM(med_total) from bill where cust_contact= %s and cust_date=%s "
        mycursor.execute(ins_cust,(c.cust_contact,c.cust_date))
        myresult2 = mycursor.fetchone()
        print("Total payable:", myresult2[0])#displaying total payable
        #updating bill into bill history table
        ins_bilhist = "INSERT INTO bill_hist (cust_name,cust_contact,cust_date,cust_address,cust_docref, total) VALUES (%s,%s,%s,%s,%s,%s)"
        val_bilhist= (c.cust_name,c.cust_contact,c.cust_date,c.cust_address,c.cust_docref,myresult2[0])
        mycursor.execute(ins_bilhist,val_bilhist)
        mydb.commit()

#dele() is used to delete records from the inventory
def dele():
    dele_ref=False
    while(dele_ref==False):
        try:
            del_refno=int(input("Enter the record reference number that you want to delete:"))
        except ValueError:
            print("Enter Valid reference number.")
            dele_ref=False
        else:
            dele_ref=True
    mycursor.execute("SELECT ref_no FROM med_inv WHERE ref_no=%s",(del_refno,))
    ref_present=mycursor.fetchone() 
    if(not ref_present):#checking presence of record
        print("\nRecord not present.")
    else:        
        del_medin = "DELETE FROM med_inv WHERE ref_no = %s" #deleting the record via MySQL query
        mycursor.execute(del_medin,(del_refno,))
        mydb.commit()
        print("\nMedicine record was successfully deleted.")
        
#disp() is used to display the inventory of pharmacy
def disp():
    #Selecting data from inventory
    mycursor.execute("SELECT * FROM med_inv order by ref_no")
    myresult = mycursor.fetchall()
    #displaying inventory in tabular form
    print(tabulate(myresult,headers = ["Ref No: ","Company Name","Medicine Type","Medicine Name","Quantity","Cost"], tablefmt='psql',numalign="left"))

#del_b() func deletes the med_name record of customer
def del_b():
    del_medname=input("\nEnter the medicine name that you want to delete:")
    mycursor.execute("SELECT med_name FROM bill WHERE med_name=%s",(del_medname,))
    med_present=mycursor.fetchone()
    if(not med_present):#checking presence of record
        print("\nRecord not present.")
    else:
        mycursor.execute("SELECT med_qnt FROM bill WHERE med_name=%s",(del_medname,))
        med_qnt=mycursor.fetchone()
        mycursor.execute("UPDATE med_inv set m_qnt=m_qnt+%s where m_name=%s",(med_qnt[0],del_medname,))#updating the quantity changes in inventory
        del_med = "DELETE FROM bill WHERE med_name = %s "
        mycursor.execute(del_med,(del_medname,))
        mydb.commit()
        print("\nMedicine record was successfully deleted.")

#displaying customer details
def findbill(): 
    ValidNO=False
    while(ValidNO==False):#checking validity of contact number
        find_contact=input("Enter contact of customer: ")
        if (len(find_contact)==10 and find_contact.isnumeric()):
              
            ValidNO=True
        else :
            print ("Invalid Contact Number entered.")
            ValidNO=False
    ValidDate=False
    while(ValidDate==False):#checking validity of date
        find_date=input("Enter date (DD/MM/YYYY) of bill: ")
        if(isValidDate(find_date)==False):
            ValidDate=False
            print("Invalid Date entered.\n")
        else:
            ValidDate=True   
    mycursor.execute("SELECT * from bill_hist where cust_date=%s and cust_contact=%s",(find_date,find_contact,))
    find_cust=mycursor.fetchall()#customer details in find_cust
    mycursor.execute("SELECT med_name,med_qnt,med_cost,med_total from bill where cust_date=%s and cust_contact=%s",(find_date,find_contact,))
    find_meds=mycursor.fetchall()#medicine details in find_cust
    if(not find_cust or not find_meds):#checking presence of records
        print("\nCustomer/Medicinal record not found!")
    else:
        print("\nCUSTOMER DETAILS: \n")#Displaying the bill and customer details
        print(tabulate(find_cust,headers = ["Customer Name","Contact","Purchase Date","Address","Reference","Total Amt"], tablefmt='psql',numalign="left"))
        print("\nMEDICINE PURCHASE DETAILS: \n")
        print(tabulate(find_meds,headers = ["Medicine Name","Qnt.","Cost per item","Total Cost"], tablefmt='psql',numalign="left"))

#display sale history through sale_hist()
def sale_hist():
    d=input("Enter the date (DD/MM/YYYY) for which you want to view sale history:")
    if(isValidDate(d)==True):#check validity of date
        mycursor.execute("SELECT cust_name,cust_contact,total from bill_hist WHERE cust_date=%s",(d,)) 
        sale=mycursor.fetchall()
        if(not sale):#check if records are present
            print("\nRecords for the date ",d," not found!!")
        else:#printing particulars of the sale history
            print(tabulate(sale,headers = ["Customer Name","Contact","Total Amt"], tablefmt='psql',numalign="left"))
    else:
        print("Invalid Date entered.\n")
        sale_hist()

#isValidDate checks validity of date
def isValidDate(inputDate):
    try:
        day,month,year = inputDate.split('/')
    except ValueError :
        return False
    else:
        try :
            datetime.datetime(int(year),int(month),int(day))
        except ValueError :
            return False
        else:
            return True

#mainpg() function is the first page that presents the functions user may want to use
def mainpg():
    print("\n**************************")
    print("PHARMACY MANAGEMENT SYSTEM")
    print("**************************\n")
    #displaying options of functions that user may want to perform
    print("1. Display Inventory\n2. Add medicine to inventory\n3. Delete Medicine from inventory\n4. Generate Bill\n5. Find bill\n6. View Sale History\n7. Exit")
    choice1=int(input("\nEnter the function you want to perform:"))#Allows user to perform respective functions
    print("\n")
    if(choice1==1):
        #Display inventory
        disp()
        mainpg()
    elif(choice1==2):
        #Add a medicine to inventory
        #Accepting medicine details
        present=True
        while(present==True):
            Ref_bool=True
            while(Ref_bool==True):
                try:
                    ref_no=int(input("Enter medicine reference number: "))
                except ValueError :
                    print("Please enter Valid Reference number.")
                    Ref_bool=True
                else:
                    Ref_bool=False
            mycursor.execute("SELECT ref_no FROM med_inv order by ref_no")
            ref_rows = mycursor.fetchall() 
            if (any(ref_no in i for i in ref_rows)) :
                print("Record with this reference number already present.")
                present=True
            else:
                present=False
        comp_name=input("Enter medicine company name: ")
        med_type=input("Enter medicine type: ")
        m_name=input("Enter medicine name: ")
        m_qnt=input("Enter medicine quantity: ")
        m_cost=input("Enter medicine cost per unit: ")   
        m1=med(ref_no,comp_name,med_type,m_name,m_qnt,m_cost)
        m1.add()#medicine details passed to add() function
        mainpg()
    elif(choice1==3):
        #Delete a medicine from Inventory
        dele()
        mainpg()
    elif(choice1==4):
        #Customer details input accepted
        cust_name=input("Enter customer name: ")
        
        ValidNO=False
        while(ValidNO==False):
            cust_contact=input("Enter customer contact: ")
            if (len(cust_contact)==10 and cust_contact.isnumeric()):#Check validity of phone number
                   
                ValidNO=True
            else :
                print ("Invalid Contact Number entered.")
                ValidNO=False
        ValidDate=False
        while(ValidDate==False):#Check validity of date
            cust_date=input("Enter date (DD/MM/YYYY) of purchase: ")
            if(isValidDate(cust_date)==False):
                print("Invalid Date entered.\n")
                ValidDate=False
            else:
                ValidDate=True
        cust_address=input("Enter customer address: ")
        cust_docref=input("Enter customer's doctor referal: ")
        b1=bills(cust_name,cust_contact,cust_date,cust_address,cust_docref)
        b1.bill_ch()#Customer details passed to bill_ch() to add/del/generate bill
    elif(choice1==5):
        #find/display a particular customer's bill on particular date
        findbill()
        mainpg()
    elif(choice1==6):
        #display sale history of a particular date
        sale_hist()
        mainpg()
    elif(choice1==7):
        #Exit from the execution
        exit()
    else:
        #Invalid Option chosen
        print("Invalid choice.")
        mainpg()

def login():#login fn 
    print("***********************************************************")
    print("WELCOME TO HEALTH24 PHARMACY".ljust(10)) 
    print("***********************************************************\n")
    print("LOGIN TO SYSTEM:\n")
    username= input("Enter username(employee I-D): ")#Accepting username
    pswrd= input("Enter password: ")#Accepting password
    mycursor.execute("SELECT * from login")#select query 
    check=mycursor.fetchall()    #check has tuples within tuples  
    if ((any(username in i for i in check))and (any(pswrd in i for i in check))) : #check the occurrence of username and password in table
        print("Login Successful!!\n")
    else :
        print("!!Invalid Credentials. Access denied!!")
        print("___________________________________________________________\n")
        login()#allows relogin incase of invalid credentials

#call of login() to begin execution
login()

#call of mainpg() to proceed of execution
mainpg()