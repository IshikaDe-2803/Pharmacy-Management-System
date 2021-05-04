from tabulate import tabulate #tabulate module--> display table in proper format
import mysql.connector #connectingm ysql with python
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Rootpass123*",
  database="medical_inventory",
)
mycursor = mydb.cursor() #creating mycursor object to access database elements
#class med defines the medical inventory
class med:
    def __init__(medi, ref_no,comp_name,med_type,m_name,m_qnt,m_cost):
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
        mycursor.execute(ins_medin,val_medin)
        mydb.commit()
        print("\nMedicine record successfully inserted.")
class bills:
    def __init__(c, cust_name,cust_contact,cust_date,cust_address,cust_docref):
        c.cust_name=cust_name
        c.cust_contact=cust_contact
        c.cust_date=cust_date
        c.cust_address=cust_address
        c.cust_docref=cust_docref
    def bill_ch(c):
        print("\n1.Add medicine to cart\n2.Delete medicine from cart\n3.Generate bill\n")
        ch2=int(input("Enter choice: "))
        if(ch2==1):
            c.add_b()
            print("\nMedicine successfully added.")
            c.bill_ch()
        elif(ch2==2):
            del_b()
            c.bill_ch()
        elif(ch2==3):
            c.disp_b()
            mainpg()
        else:
            print("\nInvalid choice.")
            c.bill_ch()
    def add_b(c):
        m_n=input("Enter the medicine name- ")
        mycursor.execute("SELECT EXISTS(SELECT m_name from med_inv where m_name=%s)",(m_n,))
        myresult3=mycursor.fetchone()
        mycursor.execute("SELECT m_qnt from med_inv where m_name=%s",(m_n,))
        quant=mycursor.fetchone()
        if((myresult3[0]==0) and (quant[0]>0) ): #checking availability of medicine
            print("Medicine not available.")
            c.add_b()
        else:
            mycursor.execute("SELECT m_cost from med_inv where m_name=%s",(m_n,))
            m_cst=mycursor.fetchone()
            m_q=int(input("Enter the medicine quantity- "))
            #update inventory
            mycursor.execute("UPDATE med_inv set m_qnt=m_qnt-%s where m_name=%s",(m_q,m_n,))
            ins_bil = "INSERT INTO bill (cust_date,cust_contact,med_name,med_qnt,med_cost,med_total) VALUES (%s,%s,%s,%s,%s,%s)"
            val_bil= (c.cust_date,c.cust_contact,m_n,m_q,m_cst[0],m_cst[0]*m_q)
            mycursor.execute(ins_bil,val_bil)
            mydb.commit()
            print("Customer record added.")
    def disp_b(c):
        print("Customer Name: ", c.cust_name)
        print("Customer Contact: ", c.cust_contact)
        print("Date of purchase: ",c.cust_date)
        print("Customer Address: ", c.cust_address)
        print("Doctor referral: ", c.cust_docref)
        mycursor.execute("SELECT med_name,med_qnt,med_cost,med_total FROM bill where cust_contact=%s and cust_date=%s",(c.cust_contact,c.cust_date,))
        myresult1 = mycursor.fetchall() 
        print(tabulate(myresult1,headers = ["Medicine Name","Quantity","Cost per item","Total Cost"], tablefmt='psql',numalign="left"))
        ins_cust= "SELECT SUM(med_total) from bill where cust_contact= %s and cust_date=%s "
        mycursor.execute(ins_cust,(c.cust_contact,c.cust_date))
        myresult2 = mycursor.fetchone()
        print("Total payable:", myresult2[0])
        ins_bilhist = "INSERT INTO bill_hist (cust_name,cust_contact,cust_date,cust_address,cust_docref, total) VALUES (%s,%s,%s,%s,%s,%s)"
        val_bilhist= (c.cust_name,c.cust_contact,c.cust_date,c.cust_address,c.cust_docref,myresult2[0])
        mycursor.execute(ins_bilhist,val_bilhist)
        mydb.commit()
#dele() is used to delete records from the inventory
def dele():
    del_refno=int(input("\nEnter the record reference number that you want to delete:"))
    del_medin = "DELETE FROM med_inv WHERE ref_no = %s"
    mycursor.execute(del_medin,(del_refno,))
    mydb.commit()
    print("\nMedicine record was successfully deleted.")
#disp() is used to display the inventory of pharmacy
def disp():
    #Selecting data from inventory
    mycursor.execute("SELECT * FROM med_inv")
    myresult = mycursor.fetchall()
    print(tabulate(myresult,headers = ["Ref No: ","Company Name","Medicine Type","Medicine Name","Quantity","Cost"], tablefmt='psql',numalign="left"))
#del_b() func deletes the med_name record of customer
def del_b():
    del_medname=input("\nEnter the medicine name that you want to delete:")
    del_med = "DELETE FROM bill WHERE med_name = %s "
    mycursor.execute(del_med,(del_medname,))
    mydb.commit()
    print("\nMedicine record was successfully deleted.")
#displaying customer details
def findbill():
    find_contact=input("Enter contact of customer: ")
    find_date=input("Enter date (DD-MM-YYYY) of bill: ")
    mycursor.execute("SELECT * from bill_hist where cust_date=%s and cust_contact=%s",(find_date,find_contact,))
    find_cust=mycursor.fetchall()
    print("\nCUSTOMER DETAILS: \n")
    print(tabulate(find_cust,headers = ["Customer Name","Contact","Purchase Date","Address","Reference","Total Amt"], tablefmt='psql',numalign="left"))
    mycursor.execute("SELECT med_name,med_qnt,med_cost,med_total from bill where cust_date=%s and cust_contact=%s",(find_date,find_contact,))
    find_meds=mycursor.fetchall()
    print("\nMEDICINE PURCHASE DETAILS: \n")
    print(tabulate(find_meds,headers = ["Medicine Name","Qnt.","Cost per item","Total Cost"], tablefmt='psql',numalign="left"))
#display sale history through sale_hist()
def sale_hist():
    d=input("Enter the date (DD-MM-YYYY) for which you want to view sale history:")
    mycursor.execute("SELECT cust_name,cust_contact,total from bill_hist WHERE cust_date=%s",(d,))
    sale=mycursor.fetchall()
    print(tabulate(sale,headers = ["Customer Name","Contact","Total Amt"], tablefmt='psql',numalign="left"))
#mainpg() function is the first page that presents the functions user may want to use
def mainpg():
    print("\n**************************")
    print("PHARMACY MANAGEMENT SYSTEM")
    print("**************************\n")
    #displaying options of functions that user may want to perform
    print("1. Display Inventory\n2. Add medicine to inventory\n3. Delete Medicine from inventory\n4. Generate Bill\n5. Find bill\n6. View Sale History\n7. Exit")
    choice1=int(input("\nEnter the function you want to perform:"))
    print("\n")
    if(choice1==1):
        #Display inventory
        disp()
        mainpg()
    elif(choice1==2):
        #Add a medicine to inventory
        ref_no=input("Enter medicine reference number: ")
        comp_name=input("Enter medicine company name: ")
        med_type=input("Enter medicine type: ")
        m_name=input("Enter medicine name: ")
        m_qnt=input("Enter medicine quantity: ")
        m_cost=input("Enter medicine cost per unit: ")   
        m1=med(ref_no,comp_name,med_type,m_name,m_qnt,m_cost)
        m1.add()
        mainpg()
    elif(choice1==3):
        #Delete a medicine from Inventory
        dele()
        mainpg()
    elif(choice1==4):
        cust_name=input("Enter customer name: ")
        cust_contact=input("Enter customer contact: ")
        cust_date=input("Enter date of purchase: ")
        cust_address=input("Enter customer address: ")
        cust_docref=input("Enter customer's doctor referal: ")
        b1=bills(cust_name,cust_contact,cust_date,cust_address,cust_docref)
        b1.bill_ch()
    elif(choice1==5):
        #find/display a particular customer's bill on particular date
        findbill()
        mainpg()
    elif(choice1==6):
        #display sale history
        sale_hist()
        mainpg()
    elif(choice1==7):
        #Exit from the execution
        exit()
    else:
        #Invalid Option chosen
        print("Invalid choice.")
        mainpg()

def login():
    print("***********************************************************")
    print("WELCOME TO HEALTH24 PHARMACY".ljust(10)) 
    print("***********************************************************\n")
    print("LOGIN TO SYSTEM:\n")
    username= input("Enter username(employee I-D): ")
    pswrd= input("Enter password: ")
    mycursor.execute("SELECT * from login")
    check=mycursor.fetchall()    #check has tuples within tuples  
    if ((any(username in i for i in check))and (any(pswrd in i for i in check))) : #check the occurrence of username and password
        print("Login Successful!!\n")
    else :
        print("!!Invalid Credentials. Access denied!!")
        print("___________________________________________________________\n")
        login()
#call of login() to begin execution
login()
#call of mainpg() to proceed of execution
mainpg()