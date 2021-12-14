import os
import pandas as pd
import sqlite3
from sqlite3 import Error
import datetime as dt
import numpy as np


class Database:
    def __init__(self, filename=None):
        if filename:
            self.conn = Database.connect(filename)
            self.cur = self.conn.cursor()
        else:
            self.conn = None
            self.cur = None


    @staticmethod
    def connect(filename):
        """connect connects to database `filename`
        If `filename` does not exist, it will be created.""" 
        try:
            conn = sqlite3.connect(filename)
        except Error as e:
            print(e)
        return conn

    def file_to_db(self,filename,fields):
        """Adds `filename` to the database"""
        location = fields["location"]
        year = fields["year"]
        payperiod = fields["payperiod"]
        if self.is_file_in_db(filename):
            print("File {} is in database already.".format(filename))
            ret_val = -1
        else:
            sql_string = "INSERT INTO tbl_file(filename,location,year,payperiod) VALUES('{}','{}','{}','{}')".format(filename,location,year,payperiod)
            try:
                self.cur.execute(sql_string)
                ret_val = self.cur.lastrowid
            except:
                print("Cannot add file to the database. Cancelling.")
                ret_val = -2
            self.conn.commit()
        return ret_val

    def delete_file(self,directory,filename):
        if self.is_file_in_db(filename):
            sql_string = "DELETE FROM tbl_file WHERE filename = '{}'".format(filename)
            try:
                self.cur.execute(sql_string)
            except:
                print("Could not delete file from database.")
            self.conn.commit()
            os.remove(directory+filename)    
        else:
            print("File not in database")

    def is_file_in_db(self,filename):

        sql_string = "SELECT id FROM tbl_file WHERE filename='{}'".format(filename)
        try:
            self.cur.execute(sql_string)
        except:
            print("Cannot access database.")

        file_id = self.cur.fetchone()

        return True if file_id else False

    def get_filenames_locations(self):
        sql_string = "SELECT filename,location,keyword,name FROM tbl_file f LEFT JOIN tbl_hlp_file_keyword h ON f.id=h.file_id LEFT JOIN tbl_keyword k ON h.keyword_id=k.id LEFT JOIN tbl_hlp_file_person hp ON f.id=hp.file_id LEFT JOIN tbl_person p ON hp.person_id=p.id;"
        try:
            self.cur.execute(sql_string)
        except:
            print("Cannot access database.")

        filename_location = self.cur.fetchall()

        return pd.DataFrame(filename_location)

    def get_location(self,filename):
        sql_string = "SELECT location FROM tbl_file WHERE filename='{}'".format(filename)
        try:
            self.cur.execute(sql_string)
        except:
            print("Cannot access database.")

        location = self.cur.fetchone()

        return location[0]

    def update_location(self, filename, location):
        sql_string = "UPDATE tbl_file SET location = '{}' WHERE filename = '{}'".format(location, filename)
        try:
            self.cur.execute(sql_string)
            ret_val = 0
        except:
            print("Cannot access database.")
            ret_val = -1
        self.conn.commit()
        return ret_val        

    def get_latest_id(self):
        sql_string= "SELECT id from tbl_file ORDER BY id DESC LIMIT 1;"
        try:                            
            self.cur.execute(sql_string)
        except:                             
            print("Cannot access database.")
        lastid = self.cur.fetchone()
        if lastid:
            return int(lastid[0])
        else:
            return 0

    def is_keyword_in_db(self,keyword):

        sql_string = "SELECT id FROM tbl_keyword WHERE keyword='{}'".format(keyword)
        try:
            self.cur.execute(sql_string)
        except:
            print("Cannot access database.")

        keyword_id = self.cur.fetchone()

        return True if keyword_id else False

    def keyword_unused(self,keyword):
        if self.is_keyword_in_db(keyword):
            sql_string = "SELECT * FROM tbl_hlp_file_keyword JOIN tbl_keyword ON keyword_id=tbl_keyword.id WHERE tbl_keyword.keyword = '{}'".format(keyword)
            try:
                self.cur.execute(sql_string)
            except:
                print("Cannot access database.")
            uses = self.cur.fetchall()
            if len(uses) == 0:
                ret_val = True
            else:
                ret_val = False
        else:
            ret_val = True

        return ret_val


    def list_keywords(self):
        sql_string = "SELECT id, keyword FROM tbl_keyword"
        try:
            self.cur.execute(sql_string)
        except:
            print("Cannot access database.")

        keywords = self.cur.fetchall()

        return pd.DataFrame(keywords,columns=["id","keyword"])


    def get_keywords(self,year):
        sql_string =  "SELECT keyword,count(keyword) FROM tbl_file f JOIN tbl_hlp_file_keyword h ON f.id=h.file_id JOIN tbl_keyword k ON h.keyword_id=k.id WHERE year={} GROUP BY keyword;".format(year)
        try:
            self.cur.execute(sql_string)
        except:
            print("Cannot access database.")

        keywords = self.cur.fetchall()

        return dict(keywords) 


    def get_person(self,year):
        sql_string =  "SELECT name,count(name) FROM tbl_file f JOIN tbl_hlp_file_person h ON f.id=h.file_id JOIN tbl_person p ON h.person_id=p.id WHERE year={} GROUP BY name;".format(year)
        try:
            self.cur.execute(sql_string)
        except:
            print("Cannot access database.")

        persons = self.cur.fetchall()

        return dict(persons) 


    def get_years(self):
        sql_string = "SELECT DISTINCT year FROM tbl_file;"
        try:
            self.cur.execute(sql_string)
        except:
            print("Cannot access database to get years.")

        years = list(self.cur.fetchall())

        return years




    def keywords_on_file(self, filename):
        sql_string = "SELECT f.id,k.keyword FROM tbl_file f JOIN tbl_hlp_file_keyword h ON f.id=h.file_id JOIN tbl_keyword k ON h.keyword_id=k.id WHERE filename='{}'".format(filename)
        try:
            self.cur.execute(sql_string)
        except:
            print("Cannot access database.")

        keywords = self.cur.fetchall()

        return pd.DataFrame(keywords,columns=["id","keyword"])


    def persons_on_file(self, filename):
        sql_string = "SELECT f.id,p.name FROM tbl_file f JOIN tbl_hlp_file_person h ON f.id=h.file_id JOIN tbl_person p ON h.person_id=p.id WHERE filename='{}'".format(filename)
        try:
            self.cur.execute(sql_string)
        except:
            print("Cannot access database.")

        persons = self.cur.fetchall()

        return pd.DataFrame(persons,columns=["id","person"])


    def delete_keyword(self,keyword):
        kw_in_db = self.is_keyword_in_db(keyword)
        kw_unused = self.keyword_unused(keyword)
        if kw_in_db and kw_unused:
            sql_string = "DELETE FROM tbl_keyword WHERE keyword = '{}'".format(keyword)
            try:
                self.cur.execute(sql_string)
            except:
                print("Could not delete keyword from database.")
            self.conn.commit()
        elif kw_in_db and not kw_unused:
            print(keyword,"in use, it cannot be deleted.")
            return -1
        else:
            print("Keyword not in database")


    def add_person(self,person):
        """Adds `person` to the database"""
        # if self.is_keyword_in_db(keyword):
            # print("Keyword {} is in database already.".format(keyword))
            # ret_val = -1
        # else:
        sql_string = "INSERT INTO tbl_person(name) VALUES('{}')".format(person)
        try:
            self.cur.execute(sql_string)
            ret_val = self.cur.lastrowid
        except:
            print("Cannot add person to the database. Cancelling.")
            ret_val = -2
        self.conn.commit()
        return ret_val


    def add_keyword(self,keyword):
        """Adds `filename` to the database"""
        if self.is_keyword_in_db(keyword):
            print("Keyword {} is in database already.".format(keyword))
            ret_val = -1
        else:
            sql_string = "INSERT INTO tbl_keyword(keyword) VALUES('{}')".format(keyword)
            try:
                self.cur.execute(sql_string)
                ret_val = self.cur.lastrowid
            except:
                print("Cannot add keyword to the database. Cancelling.")
                ret_val = -2
            self.conn.commit()
        return ret_val


    def add_person_to_file(self,filename,person):
        self.add_person(person)
        sql_string1 = "SELECT id FROM tbl_file WHERE filename='{}'".format(filename)
        sql_string2 = "SELECT id FROM tbl_person WHERE name='{}'".format(person)
        try:
            self.cur.execute(sql_string1)
        except:
            print("Could not get file from database.")
        fileid = self.cur.fetchone() 
        try:
            self.cur.execute(sql_string2)
        except:
            print("Could not get person from database.")
        personid = self.cur.fetchone() 
        print(personid) 
        sql_string3 = "INSERT INTO tbl_hlp_file_person (file_id,person_id) VALUES ('{}','{}')".format(fileid[0],personid[0])

        try:
            self.cur.execute(sql_string3)
        except:
            print("Could not insert person to database.")
        self.conn.commit()



    def add_keyword_to_file(self,filename,keyword):
        sql_string1 = "SELECT id FROM tbl_file WHERE filename='{}'".format(filename)
        sql_string2 = "SELECT id FROM tbl_keyword WHERE keyword='{}'".format(keyword)
        try:
            self.cur.execute(sql_string1)
        except:
            print("Could not delete keyword from database.")
        fileid = self.cur.fetchone() 
        try:
            self.cur.execute(sql_string2)
        except:
            print("Could not delete keyword from database.")
        keywordid = self.cur.fetchone() 
        
        sql_string3 = "INSERT INTO tbl_hlp_file_keyword (file_id,keyword_id) VALUES ('{}','{}')".format(fileid[0],keywordid[0])

        try:
            self.cur.execute(sql_string3)
        except:
            print("Could not delete keyword from database.")
        self.conn.commit()


    def delete_keyword_from_file(self,filename, keyword):
        sql_string = "SELECT h.rowid FROM tbl_file f JOIN tbl_hlp_file_keyword h ON f.id=h.file_id JOIN tbl_keyword k ON h.keyword_id=k.id WHERE f.filename='{}' AND k.keyword='{}'".format(filename,keyword)
        try:
            self.cur.execute(sql_string)
        except:
            print("Could not connect to database.")
        rowid = self.cur.fetchone() 
        sql_string_del = "DELETE FROM tbl_hlp_file_keyword WHERE rowid='{}'".format(rowid[0])
        try:
            self.cur.execute(sql_string_del)
        except:
            print("Could not connect to database.")
        self.conn.commit() 

    def delete_person_from_file(self,filename, person):
        sql_string = "SELECT h.rowid FROM tbl_file f JOIN tbl_hlp_file_person h ON f.id=h.file_id JOIN tbl_person p ON h.person_id=p.id WHERE f.filename='{}' AND p.name='{}'".format(filename,person)
        try:
            self.cur.execute(sql_string)
        except:
            print("Could not connect to database.")
        rowid = self.cur.fetchone() 
        sql_string_del = "DELETE FROM tbl_hlp_file_person WHERE rowid='{}'".format(rowid[0])
        try:
            self.cur.execute(sql_string_del)
        except:
            print("Could not connect to database.")
        self.conn.commit() 
 
