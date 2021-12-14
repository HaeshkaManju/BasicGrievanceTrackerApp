import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class LabelInput(tk.Frame):
    """A widget, containing a label and input together.
    This class is taken from the book 'Python GUI Programming with Tkinter' by Alan D. Moore"""
    def __init__(self, parent, label='', input_class=ttk.Entry,
            input_var=None, input_args=None, label_args=None, **kwargs):
        super().__init__(parent,**kwargs)
        input_args = input_args or {}
        label_args = label_args or {}
        self.variable = input_var

        if input_class in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton):
            input_args["text"] = label
            input_args["variable"] = input_var
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))
            input_args["textvariable"] = input_var

        self.input = input_class(self, **input_args)
        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
        self.columnconfigure(0, weight=1)

    def grid(self, sticky=(tk.E + tk.W), **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def get(self):
        try:
            if self.variable:
                return self.variable.get()
            elif type(self.input) == tk.Text:
                return self.input.get('1.0',tk.END)
            else:
                return self.input.get()
        except (TypeError, tk.TclError):
            # happens when numeric fields are empty.
            return ''

    def set(self, value, *args, **kwargs):
        if type(self.variable) == tk.BooleanVar:
            self.variable.set(bool(value))
        elif self.variable:
            self.variable.set(value, *args, **kwargs)
        elif type(self.input) in (ttk.Checkbutton, ttk.Radiobutton):
            if value:
                self.input.select()
            else:
                self.input.deselect()
        elif type(self.input) == tk.Text:
            self.input.delete('1.0',tk.END)
            self.input.insert('1.0',value)
        else:
            self.input.delete(0, tk.END)
            self.input.insert(0, value)


class ValidatedMixin:
    """Adds a validation functionality to an input widget.
        Taken from 'Python GUI programming with Tkinter' by Alan D. Moore"""

    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)
        
        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)

        self.config(
                validate='all',
                validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
                invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
        )

    def _toggle_error(self, on=False):
        self.config(foreground=('red' if on else 'black'))

    def _validate(self, proposed, current, char, event, index, action):
        self._toggle_error(False)
        self.error.set('')
        valid = True
        if event == 'focusout':
            valid = self._focusout_validate(event=event)
        elif event == 'key':
            valid = self._key_validate(proposed=proposed, current=current, char=char, event=event, index=index, action=action)
        return valid

    def _focusout_validate(self, **kwargs):
        return True

    def _key_validate(self, **kwargs):
        return True

    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'focusout':
            self._focusout_invalid(event=event)
        elif event == 'key':
            self._key_invalid(proposed=proposed, current=current, char=char, event=event, index=index, action=action)

    def _focusout_invalid(self, **kwargs):
        self._toggle_error(True)

    def _key_invalid(self, **kwargs):
        pass

    def trigger_focusout_validation(self):
        valid = self._validate('', '', '', 'focusout', '', '')
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid


class MainMenu(tk.Menu):
    """The Application's main menu"""
    def __init__(self,parent,  callbacks, **kwargs):
        super().__init__(parent, **kwargs)

        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label="Quit", command=callbacks['file->quit'])
        self.add_cascade(label='File', menu=file_menu)

        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label="About...", command=self.show_about)
        self.add_cascade(label='Help', menu=help_menu)

    def show_about(self):
        """Show an about dialog"""
        message = "Union Grievance Tracker"
        detail = ('provided by Sascha Schmidt\n'
                'For assistance and future extensions, please contact the author.')
        messagebox.showinfo(title='About', message=message, detail=detail)




class MainView(tk.Frame):
    """Main view of the application"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.inputs = {} # Dict, which holds the inputs
        parent.update_idletasks()
        title_view = TitleView(self)
        title_view.grid(row=0,column=0,columnspan=2,sticky=(tk.N+tk.E+tk.S+tk.W))
        self.nav_view = NavigationView(self)
        self.nav_view.grid(row=1,column=0,sticky=(tk.N+tk.S+tk.W))

        self.content_view = []
        parent.update_idletasks()
        self.content_view.append(ContentView_upload(self))
        self.content_view.append(ContentView_search(self))
        self.content_view.append(ContentView_keywords(self))
        self.content_view.append(ContentView_graphics(self))
        self.content_view.append(ContentView_details(self))
        self.content_view[0].grid(row=1,column=1,sticky=(tk.N+tk.E+tk.S+tk.W))
        self.columnconfigure(1,weight=1)
        self.rowconfigure(1,weight=1)


    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            if type(widget) == list:
                data[key] = []
                for cnt in range(len(widget)):
                    data[key].append(widget[cnt].get())
            else:
                data[key] = widget.get()
        return data

class TitleView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        heading = ttk.Label(self,text="Union Grievance Tracker\nHome Page",width=100,justify="center",padding=(300,10))
        heading.pack(fill='x',expand=True)


class NavigationView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.buttons = []
        button_labels = ["Upload","Search","Keywords","Graphics"]
        for label in button_labels:
            self.buttons.append(ttk.Button(self,text=label))

        for but in self.buttons:
            # but.grid(column=0,sticky=(tk.N+tk.E+tk.W+tk.S))
            but.pack(fill='x',padx=10,side='top')

class ContentView_upload(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Variable to hold the filename of a new file
        self.var_filename = tk.StringVar()
        self.var_serialno = tk.IntVar()
        self.var_location = tk.StringVar()
        self.var_year = tk.IntVar(value=2021)
        self.var_payperiod = tk.IntVar()

        heading = ttk.Label(self,text="Upload" )
        heading.grid(row=1,padx=(50,5),pady=(20,10),sticky=(tk.N+tk.S+tk.E+tk.W))

        self.but_get_filename = ttk.Button(self,text='Select file...')
        self.but_get_filename.grid(row=2,column=0,padx=(50,5),pady=5,sticky=(tk.N+tk.S+tk.E+tk.W))

        self.inp_filename = ttk.Entry(self,state="readonly",takefocus=False, textvariable=self.var_filename)
        self.inp_filename.grid(row=3,column=0,padx=(50,5),pady=(5,20),sticky=(tk.N+tk.S+tk.E+tk.W))
        
        self.but_upload_file = ttk.Button(self, text="Upload file")
        self.but_upload_file.grid(row=6,column=0,padx=(50,5),pady=(50,20),sticky=(tk.N+tk.S+tk.E+tk.W))

        # self.inp_serialno = LabelInput(self,'Serial Number',input_var=self.var_serialno)
        # self.inp_serialno.grid(row=4, column=0, padx=(50,5), pady=5)

        self.inp_location = LabelInput(self,'Location',input_var=self.var_location)
        self.inp_location.grid(row=5, column=0, padx=(50,5), pady=5)

        self.inp_year = LabelInput(self,'Year',input_var=self.var_year)
        self.inp_year.grid(row=5, column=1, padx=(5,5), pady=5)

        pay_period = ["{}".format(x) for x in range(1,27)]
        self.inp_payperiod = LabelInput(self,'Payment period',input_class=ttk.Combobox, input_var=self.var_payperiod, input_args={"values":pay_period})
        self.inp_payperiod.grid(row=5, column=2, padx=(5,5), pady=5)


class ContentView_search(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.ico_cross = tk.PhotoImage(file='icons/cross.png').subsample(2,2)
        self.ico_eye = tk.PhotoImage(file='icons/eye.png').subsample(2,2) 

        self.var_searchterm = tk.StringVar()

        heading = ttk.Label(self,text="Search")
        heading.grid(row=1,padx=(50,5),pady=(20,10),sticky=(tk.N+tk.S+tk.E+tk.W))

        self.inp_search = ttk.Entry(self, textvariable=self.var_searchterm)
        self.inp_search.grid(row=2,column=0,padx=(50,5),pady=5,sticky=(tk.N+tk.S+tk.E+tk.W))
        self.but_search = ttk.Button(self, text="Search")
        self.but_search.grid(row=2, column=1, padx=(5,5))

        self.frm_res = tk.Frame(self)
        self.frm_res.grid(row=3,column=0,columnspan=4,padx=(50,5),sticky=(tk.N+tk.S+tk.E+tk.W))

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=1)
        self.columnconfigure(3,weight=1)
        self.rowconfigure(3,weight=1) 

        self.search_result_list = []
    
    def show_results(self, results):
        self.result_rows=[]
        for item in self.frm_res.winfo_children():
            item.destroy()
        self.search_result_list=[]
        for cnt,result in enumerate(results):
            # line=ttk.Frame(self.frm_res)
            # line.grid(row=cnt,column=0)
            name=ttk.Label(self.frm_res,text=result,justify="left")
            name.grid(row=cnt,column=0,sticky=(tk.N+tk.S+tk.E+tk.W))

            but_show = tk.Button(self.frm_res,image=self.ico_eye,highlightthickness=0, bd=0,borderwidth=0,relief=tk.FLAT,width=25,height=25)
            but_show.grid(row=cnt,column=1)
            but_del = tk.Button(self.frm_res,image=self.ico_cross,highlightthickness=0, bd=0,borderwidth=0,relief=tk.FLAT,width=25,height=25)
            but_del.grid(row=cnt,column=2)

            self.search_result_list.append([cnt,result,but_show,but_del,name])

            self.frm_res.columnconfigure(0,weight=1)


class ContentView_keywords(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.ico_cross = tk.PhotoImage(file='icons/cross.png').subsample(2,2)
        self.var_keyword = tk.StringVar()

        heading = ttk.Label(self,text="Keywords")
        heading.grid(row=1,padx=(50,5),pady=(20,10),sticky=(tk.N+tk.S+tk.E+tk.W))

        self.inp_keyword = ttk.Entry(self, textvariable=self.var_keyword)
        self.inp_keyword.grid(row=2,column=0,padx=(50,5),pady=5,sticky=(tk.N+tk.S+tk.E+tk.W))
        self.but_keyword = ttk.Button(self, text="Add")
        self.but_keyword.grid(row=2, column=1, padx=(5,5))
        
        self.frm_keywords = tk.Frame(self)
        self.frm_keywords.grid(row=3,column=0,columnspan=4,padx=(50,5),sticky=(tk.N+tk.S+tk.E+tk.W))

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=1)
        self.columnconfigure(3,weight=1)
        self.rowconfigure(3,weight=1) 

        self.keywords_list = []

    def show_keywords(self, keywords):
        self.result_rows=[]
        for item in self.frm_keywords.winfo_children():
            item.destroy()
        self.keywords_list=[]
        for cnt,keyword in enumerate(keywords):
            # line=ttk.Frame(self.frm_res)
            # line.grid(row=cnt,column=0)
            name=ttk.Label(self.frm_keywords,text=keyword,justify="left")
            name.grid(row=cnt,column=0,sticky=(tk.N+tk.S+tk.E+tk.W))

            but_del = tk.Button(self.frm_keywords,image=self.ico_cross,highlightthickness=0, bd=0,borderwidth=0,relief=tk.FLAT,width=25,height=25)
            but_del.grid(row=cnt,column=2)

            self.keywords_list.append([cnt,keyword,but_del,name])

            self.frm_keywords.columnconfigure(0,weight=1)




class ContentView_graphics(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.var_sel_year=tk.IntVar(value=2021)

        heading = ttk.Label(self,text="Graphics")
        heading.grid(row=0,column=0,padx=(50,5),pady=(20,10),sticky=(tk.N+tk.S+tk.E+tk.W))

        lbl_radiogroup = ttk.Label(self,text="Select your graph:")
        lbl_radiogroup.grid(row=1,column=0,padx=(50,5),pady=5,sticky=(tk.N+tk.S+tk.E+tk.W))

        self.years = [2021,] 
        self.cmb_sel_year = LabelInput(self,'Select a year:',input_class=ttk.Combobox, input_var=self.var_sel_year, input_args={"values":self.years})
        self.cmb_sel_year.grid(row=1, column=1, rowspan=2, padx=(5,5), pady=5)

class ContentView_details(tk.Frame):
    """Other than the other content views, this class shows the details of a file"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.ico_cross = tk.PhotoImage(file='icons/cross.png').subsample(2,2)

        self.var_filename = tk.StringVar()
        self.var_location = tk.StringVar()
        self.var_person = tk.StringVar()

        heading = ttk.Label(self,text="File details")
        heading.grid(row=1,column=0, columnspan=4,padx=(50,5),pady=(20,10),sticky=(tk.N+tk.S+tk.E+tk.W))

        lbl_filename = ttk.Label(self, textvariable=self.var_filename)
        lbl_filename.grid(row=2,column=0,columnspan=2, padx=(50,5),pady=5)

        self.but_open_file = ttk.Button(self,text="Open file")
        self.but_open_file.grid(row=2,column=2)

        self.inp_location = LabelInput(self, "Location", input_class=ttk.Entry, input_var=self.var_location)
        self.inp_location.grid(row=3,column=0,columnspan=2,padx=(50,5))

        self.but_upd_location = ttk.Button(self,text="Update location")
        self.but_upd_location.grid(row=3,column=2, pady=(15,0))

        self.frm_keywords = ttk.Labelframe(self,text="Keywords")
        self.frm_keywords.grid(row=4,column=0,columnspan=2,padx=(50,5),sticky=(tk.N+tk.S+tk.E+tk.W))
        
        self.frm_persons = ttk.Labelframe(self,text="Persons involved")
        self.frm_persons.grid(row=4,column=2,columnspan=2,padx=(5,5),sticky=(tk.N+tk.S+tk.E+tk.W))

        self.inp_person = LabelInput(self, "Add person", input_class=ttk.Entry, input_var=self.var_person)
        self.inp_person.grid(row=5,column=2,padx=(5,5))

        self.but_add_person = ttk.Button(self,text="Add")
        self.but_add_person.grid(row=5,column=3, pady=(15,0))

        self.var_keywords = []
        self.cmb_keywords = ttk.Combobox(self,values=self.var_keywords)
        self.cmb_keywords.grid(row=5,column=0,padx=(50,5), pady=(15,0),sticky=(tk.N+tk.S+tk.E+tk.W))

        self.but_add_keyword = ttk.Button(self,text="Add")
        self.but_add_keyword.grid(row=5,column=1, pady=(15,0))



        self.columnconfigure(0,weight=1)
        # self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=1)
        # self.columnconfigure(3,weight=1)
        self.rowconfigure(4,weight=1) 

        self.keywords_list = []
        self.persons_list = []

    def show_keywords(self, keywords):
        self.result_rows=[]
        for item in self.frm_keywords.winfo_children():
            item.destroy()
        self.keywords_list=[]
        for cnt,keyword in enumerate(keywords):
            # line=ttk.Frame(self.frm_res)
            # line.grid(row=cnt,column=0)
            name=ttk.Label(self.frm_keywords,text=keyword,justify="left")
            name.grid(row=cnt,column=0,sticky=(tk.N+tk.S+tk.E+tk.W))

            but_del = tk.Button(self.frm_keywords,image=self.ico_cross,highlightthickness=0, bd=0,borderwidth=0,relief=tk.FLAT,width=25,height=25)
            but_del.grid(row=cnt,column=2)

            self.keywords_list.append([cnt,keyword,but_del,name])

            self.frm_keywords.columnconfigure(0,weight=1)


    def show_persons(self, persons):
        for item in self.frm_persons.winfo_children():
            item.destroy()
        self.persons_list=[]
        for cnt,person in enumerate(persons):
            # line=ttk.Frame(self.frm_res)
            # line.grid(row=cnt,column=0)
            name=ttk.Label(self.frm_persons,text=person,justify="left")
            name.grid(row=cnt,column=0,sticky=(tk.N+tk.S+tk.E+tk.W))

            but_del = tk.Button(self.frm_persons,image=self.ico_cross,highlightthickness=0, bd=0,borderwidth=0,relief=tk.FLAT,width=25,height=25)
            but_del.grid(row=cnt,column=2)

            self.persons_list.append([cnt,person,but_del,name])

            self.frm_keywords.columnconfigure(0,weight=1)
