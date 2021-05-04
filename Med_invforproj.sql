create database medical_inventory;
use medical_inventory;
create table med_inv(
ref_no integer,
comp_name char(40),
med_type char(20),
m_name char(40),
m_qnt integer,
m_cost decimal
);
select * from med_inv;
create table bill(
med_name char(40),
med_cost decimal,
sr_no integer,
cust_contact char(40) PRIMARY KEY
);
drop table bill;
create table bill(
cust_date char(15),
cust_contact char(40) ,
med_name char(40),
med_qnt integer,
med_cost decimal,
med_total decimal
);
select* from bill;
create table login(
emp_id char(40) ,
pswrd char(40) 
);
insert into login values("EM120","abcd*");
insert into login values("EM100","#log");
insert into login values("EM90","emp@123");
select* from login;
create table bill_hist(
cust_name char(40),
cust_contact char(20),
cust_date char(15),
cust_address char(40),
cust_docref char(20), 
total decimal
);
select* from bill_hist;
delete from bill where cust_date="02-05-2021";
