import os
import platform
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
# import datetime as dt
# import numpy as np
# import pandas as pd
# from . import model as m
from . import view as v
from . import database
from . import graphs as g

class Application(tk.Tk):
    """Application for the comparison of dayly data
    The Application class is the controller part of the app.
    Subclass of tk.TK, so the root of the GUI"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.title("Union Grievance Tracker")
        self.geometry("800x600")
        self.resizable(width=True, height=True)
        if platform.system()=="Windows":
            pathdelimiter = "\\"
        else: 
            pathdelimiter = "/"
        self.upload_dir = "report_files" + pathdelimiter

        """ Add views to the main window
        padx and pady in the grid methods defines the border around the widgets.
        """
        self.frame_active=0
        self.mv = v.MainView(self,background='purple')
        # self.mv.grid(sticky=(tk.N+tk.S+tk.E+tk.W))
        self.mv.pack(fill='both',expand=True)
        for cnt,but in enumerate(self.mv.nav_view.buttons):
            but.configure(command=lambda cnt=cnt: self.change_frame(cnt))

        # Connect filedialog to button
        self.mv.content_view[0].but_get_filename.configure(command=self.click_select_file)

        # Connect upload function to button
        self.mv.content_view[0].but_upload_file.configure(command=self.click_upload_file)

        # Connect search function to button
        self.mv.content_view[1].but_search.configure(command=self.click_search)
        
        # Connect keyword add function to button
        self.mv.content_view[2].but_keyword.configure(command=self.click_keyword_add)

        # Connect to the database
        self.db = database.Database('grievance_tracker/data.db')
        
        # Configure graph window
        self.var_radio_graph = tk.IntVar(value=1)
        graphs=[("Keyword Count by Year",1),
                ("Employee Issue Count by Year",2),
                ("Keyword Density",3)]
        for cnt, (key, val) in enumerate(graphs):
            opt=ttk.Radiobutton(self.mv.content_view[3],
                    text=key,
                    # padx=20,
                    variable=self.var_radio_graph,
                    command=self.update_graph,value=val)
            opt.grid(row=2+cnt,column=0,padx=(50,5),sticky=tk.W)
        
        self.mv.content_view[3].cmb_sel_year.input['values']=self.db.get_years()
        self.mv.content_view[3].cmb_sel_year.input.configure(postcommand=self.update_graph)
        self.graph = g.ChartView(self.mv.content_view[3])
        self.graph.grid(row=10, column=0, columnspan=2, padx=(50,5), sticky=(tk.N+tk.S+tk.E+tk.W))

        self.update_keywords()
        self.update_graph()

    def update_graph(self):
        year = self.mv.content_view[3].var_sel_year.get()
        keywords = self.db.get_keywords(year)
        selection = self.var_radio_graph.get()
        if selection==1:
            self.graph.draw_bars("Keyword Count {}".format(year), keywords.values(),keywords.keys())
        elif selection==2:
            person = self.db.get_person(year)
            self.graph.draw_bars("Employee Issue Count {}".format(year), person.values(),person.keys())
        elif selection==3:
            self.graph.draw_pie("Keyword Density {}".format(year), keywords.values(),keywords.keys(),None,'%1.1f%%')


    def update_keywords(self):
        self.all_keywords = self.db.list_keywords()
        self.mv.content_view[2].show_keywords(list(self.all_keywords["keyword"]))

        for cnt,keyword,but_del,label in self.mv.content_view[2].keywords_list:
            but_del.configure(command=lambda cnt=cnt: self.delete_keyword(cnt))


    def change_frame(self,frm_no):
        for frm in self.mv.content_view:
            frm.grid_forget()
        self.mv.content_view[frm_no].grid(row=1,column=1,sticky=(tk.N+tk.E+tk.S+tk.W))

    def click_select_file(self):
        filename = filedialog.askopenfilename(title="Select file to add to the database...")       
        if filename:
            self.upload_filename_dir, self.upload_filename = filename.rsplit("/",1)
            print(self.upload_filename_dir)
            self.mv.content_view[0].var_filename.set(self.upload_filename)


    def click_upload_file(self):
        fields = {}
        # fields["serial_no"] = self.mv.content_view[0].inp_serialno.get()
        fields["filename"] = self.mv.content_view[0].inp_filename.get()
        fields["location"] = self.mv.content_view[0].inp_location.get()
        fields["year"] = self.mv.content_view[0].inp_year.get()
        fields["payperiod"] = self.mv.content_view[0].inp_payperiod.get()

        if '' in fields.values():
            ans = messagebox.showwarning("Please fill all data","All information needs to be filled. Please enter missing values.")
        else:
            serial = str(fields["year"]) + "{:04d}".format(1+self.db.get_latest_id())
            new_filename = serial + " " + self.upload_filename
            shutil.copyfile(self.upload_filename_dir + "/" + self.upload_filename, self.upload_dir + new_filename)
            res = self.db.file_to_db(new_filename,fields)
            if res < 0:
                messagebox.showarning("Upload failed","File '{}' could not be stored in database".format(new_filename))
            else:
                messagebox.showinfo("Success","File '{}' has been stored to database successfully. Go to 'Search' to find and modify the record.".format(new_filename))


    def click_search(self):
        searchterm = self.mv.content_view[1].inp_search.get()
        print("Searching for {}...".format(searchterm))
        filename_location = self.db.get_filenames_locations()
        # print([any(filename_location[col].str.contains(searchterm)) for col in filename_location])
        # print(filename_location)
        if len(filename_location) == 0:
            messagebox.showwarning("No results found","No data found.")
            return
        try:
            result = set(filename_location.loc[[any(filename_location.loc[row].str.contains(searchterm)) for row in filename_location.index],0].values)
        except KeyError:
            messagebox.showwarning("No results found","No results found for searchterm '{}'.".format(searchterm))
            return

        self.mv.content_view[1].show_results(result)

        for cnt,filename,but_show,but_del,label in self.mv.content_view[1].search_result_list:
            but_show.configure(command=lambda cnt=cnt: self.show_details(cnt))
            but_del.configure(command=lambda cnt=cnt: self.delete_entry(cnt))

        self.mv.content_view[1].var_searchterm.set('')


    def click_keyword_add(self):
        keyword = self.mv.content_view[2].inp_keyword.get()
        id_no = self.db.add_keyword(keyword)
        self.update_keywords()
        self.mv.content_view[2].var_keyword.set('')

    def delete_entry(self,cnt):
        filename = self.mv.content_view[1].search_result_list[cnt][1]
        print(filename,"will be deleted.")
        self.db.delete_file(self.upload_dir,filename)
        for item in self.mv.content_view[1].search_result_list[cnt][2:]:
            item.destroy()

    def delete_keyword(self,cnt):
        keyword = self.mv.content_view[2].keywords_list[cnt][1]
        print(keyword,"will be deleted.")
        ret = self.db.delete_keyword(keyword)
        if ret != -1:
            for item in self.mv.content_view[2].keywords_list[cnt][2:]:
                item.destroy()
        else:
            messagebox.showwarning("Keyword cannot be deleted","Keyword '{}' is in use and cannot be deleted. Please delete the keyword from all files, first.".format(keyword))

    def show_details(self,cnt):
        filename = self.mv.content_view[1].search_result_list[cnt][1]
        location = self.db.get_location(filename)
        self.change_frame(4)
        self.mv.content_view[4].var_filename.set(filename)
        self.mv.content_view[4].var_location.set(location)
        self.mv.content_view[4].but_open_file.configure(command=lambda filename=filename: self.open_file(filename))
        self.mv.content_view[4].but_upd_location.configure(command=self.upd_location)
       
        self.file_keywords = self.db.keywords_on_file(filename)
        self.mv.content_view[4].show_keywords(list(self.file_keywords["keyword"]))

        for cnt,keyword,but_del,label in self.mv.content_view[4].keywords_list:
            but_del.configure(command=lambda cnt=cnt: self.delete_keyword_from_file(cnt,filename))
        
        self.mv.content_view[4].cmb_keywords.configure(values=list(self.all_keywords['keyword']))
        self.mv.content_view[4].but_add_keyword.configure(command=lambda filename=filename: self.add_keyword_to_file(filename))

        self.file_persons = self.db.persons_on_file(filename)
        self.mv.content_view[4].show_persons(list(self.file_persons["person"]))

        for cnt,person,but_del,label in self.mv.content_view[4].persons_list:
            but_del.configure(command=lambda cnt=cnt: self.delete_person_from_file(cnt,filename))
        
        self.mv.content_view[4].but_add_person.configure(command=lambda filename=filename: self.add_person_to_file(filename))

    def open_file(self,filename):
        os.startfile(self.upload_dir + filename, 'open')


    def upd_location(self):
        filename = self.mv.content_view[4].var_filename.get()
        location = self.mv.content_view[4].var_location.get()
        res = self.db.update_location(filename, location)
        if res == -1:
            messagebox.showwarning("Location could not be changed","The location could not be changed as intended")
        elif res == 0:
            messagebox.showinfo("Location updated","The location of '{}' has been updated to '{}' successfully.".format(filename, location))


    def add_keyword_to_file(self,filename):
        keyword = self.mv.content_view[4].cmb_keywords.get()
        if keyword in ([x[1] for x in self.mv.content_view[4].keywords_list]):
            messagebox.showwarning("Keyword already there","The keyword is already connected to the file")
        else:
            self.db.add_keyword_to_file(filename,keyword)
            self.file_keywords = self.db.keywords_on_file(filename)
            self.mv.content_view[4].show_keywords(list(self.file_keywords["keyword"]))
            for cnt,keyword,but_del,label in self.mv.content_view[4].keywords_list:
                but_del.configure(command=lambda cnt=cnt: self.delete_keyword_from_file(cnt,filename))


    def add_person_to_file(self,filename):
        person = self.mv.content_view[4].var_person.get()
        self.db.add_person_to_file(filename,person)
        self.file_persons = self.db.persons_on_file(filename)
        self.mv.content_view[4].show_persons(list(self.file_persons["person"]))
        self.mv.content_view[4].var_person.set('')


    def delete_keyword_from_file(self,cnt,filename):
        keyword = self.mv.content_view[4].keywords_list[cnt][1]
        self.db.delete_keyword_from_file(filename,keyword)
        self.file_keywords = self.db.keywords_on_file(filename)
        self.mv.content_view[4].show_keywords(list(self.file_keywords["keyword"]))


    def delete_person_from_file(self,cnt,filename):
        person = self.mv.content_view[4].persons_list[cnt][1]
        self.db.delete_person_from_file(filename,person)
        self.file_persons = self.db.persons_on_file(filename)
        self.mv.content_view[4].show_persons(list(self.file_persons["person"]))
