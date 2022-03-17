import tkinter as tk
from tkinter import messagebox as msg
from tkinter import ttk, Menu, Spinbox, filedialog, scrolledtext
import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib import pyplot as plt

# =====================================================#
# =======           Initial Parameters          =======#
# =====================================================#

mpl.use("TkAgg")
mpl.style.use('seaborn-bright')
root = tk.Tk()
# root.geometry("800x600")
root.resizable(True, False)
root.title('GraphMaker')

# =====================================================#
# =========           Functions Area          =========#
# =====================================================#
h_ = 1
w_ = 14
b_ = 1
fg_ = 'white'
fo_ = ("Roboto", 14, "bold")
sl_ = tk.LEFT
sr_ = tk.RIGHT
st_ = tk.TOP
sb_ = tk.BOTTOM
re_ = tk.RAISED
file_s = []


# ================| Open menu callback |================#
def openFile():
    for widget in infobox.winfo_children():
        widget.destroy()
    filename = filedialog.askopenfilename(initialdir="/", title="Select File",
                                          filetypes=(("CSV file", "*.csv"), ("All files", "*.*")))
    if filename == "":
        filename = 'No file selected\n'
    else:
        filename = filename
    file_s.append(filename)
    for file_ in file_s:
        if file_ == 'No file selected\n':
            pass
        else:
            print(file_)
    infobox.insert(tk.INSERT, file_)
    infobox.insert(tk.INSERT, '\n')


# ==============| Graph source callback |==============#
def sourceGraph(fig_d, colors_, canvas_area, tool_area, x_min=None, x_max=None, **kwargs):
    fig = Figure(figsize=fig_d, dpi=100)
    a = fig.add_subplot(111)
    global csvDf
    for file_ in file_s:
        if file_ == 'No file selected\n':
            pass
        else:
            csvDf = pd.read_csv(open(file_), names=['x_val', 'y_val'])
        global y_col
        y_col = csvDf.y_val
        global x_col
        x_col = csvDf.x_val
        if x_min == None or x_max == None:
            x_min = np.min(x_col)
            x_max = np.max(x_col)
        a.plot(x_col, y_col, color=colors_, label=grlegend.get(), linewidth=line_thik.get())
        a.legend(loc='best')
    a.set_xlim(x_min, x_max)
    a.set_xlabel(xlabel.get())
    a.set_ylabel(ylabel.get())
    a.set_title(grtitle.get())
    if radVar.get() == 0:
        pass
    elif radVar.get() == 1:
        a.grid()
    # --------------------------------------------------
    canvas = FigureCanvasTkAgg(fig, master=canvas_area)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    toolbar = NavigationToolbar2Tk(canvas, tool_area)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    return x_col, y_col, csvDf


# =============|  Plot Button function |=============#
def plotGraph():
    info_call()
    p_fig = (6, 4)
    cc_ = (color_chosen.get()).lower()
    sourceGraph(p_fig, cc_, gr_canvas, tool_canvas)


# =============| Refresh Button function |=============#
def re_fresh():
    p_fig = (6, 4)
    cc_ = (color_chosen.get()).lower()
    sec_graph_frame.destroy()
    gr_canvas = tk.Canvas(graph_frame, height=400, width=600, bg="#ffffff")
    gr_canvas.grid(column=0, row=0, columnspan=3)
    tool_canvas = tk.Canvas(graph_frame, height=45, width=600, bg="#cfcfcf")
    tool_canvas.grid(column=0, row=1, columnspan=3)
    info_call()
    sourceGraph(p_fig, cc_, gr_canvas, tool_canvas)


# ===========| Info-box output function |============#
def info_call():
    info = f'\n~Graph name: {grtitle.get()}\n' \
           f'~X-Label: {xlabel.get()}\n' \
           f'~Y-Label: {ylabel.get()}\n' \
           f'~Legend: {grlegend.get()}\n' \
           f'~Line Thickness: {line_thik.get()}\n' \
           f'~Line color: {color_chosen.get()}\n'
    infobox.insert(tk.INSERT, info)


# ===========| Message Box |============#
def _msgBox():
    msg.showinfo('About GraphMaker', 'This program was made in python with Tkinter module.\nYear of development: 2020.')


# =========| Exit GUI cleanly |=========#
def _quit():
    root.quit()
    root.destroy()
    exit()


# =====================================================#
# =========       Tkinter Functions Area      =========#
# =====================================================#
def widget_func(widget, tabName, text_, textv_, he_, wi_, command_, c_, r_, py_, px_, cs_, rs_, stik_, **kwargs):
    if widget == 'btn':
        ttk.Button(tabName, text=text_, command=command_).grid(column=c_, row=r_, pady=py_, padx=px_, columnspan=cs_,
                                                               rowspan=rs_, sticky=stik_)
    elif widget == 'label':
        ttk.Label(tabName, text=text_).grid(column=c_, row=r_, pady=py_, padx=px_, columnspan=cs_, rowspan=rs_,
                                            sticky=stik_)


# ==============| Widgets func |==============#
'''class getWidget:
    def __init__(self, widget, tabName, text_, textv, height, width, 
    command, column, row, py, px, cs, rs, stik_, **kwargs):
        self.textv = textv
        self.stik_ = stik_
        self.tabname = tabname
'''
# ======================================================================================#     ####   ####
# =======================                   Menu Area            =======================#    ##  |##|   ##
# ======================================================================================#   ##    ##     ##

# -------------------| Menu Bar |-------------------#
menu_bar = Menu(root)
root.config(menu=menu_bar)

# -------------------| File Menu |------------------#
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Load Data", command=openFile)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=_quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# -------------------| Help Menu |------------------#
help_menu = Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=_msgBox)
menu_bar.add_cascade(label="Help", menu=help_menu)

# ======================================================================================#    ##########
# =======================                   Multi-Tab             ======================#    	##
# ======================================================================================#    	##

tabControl = ttk.Notebook(root)
tab_1 = ttk.Frame(tabControl)
tabControl.add(tab_1, text=' Graph ')
tabControl.pack(expand=1, fill="both")

# #######################################################################################		##
# ####################                   Tab-1 Area            ##########################		##
# #######################################################################################		##

# =================| Graph-Canvas Frame |=================#
graph_frame = ttk.LabelFrame(tab_1, text=' Graph Canvas ')
graph_frame.grid(column=0, row=0, columnspan=3, padx=8, pady=4)
sec_graph_frame = tk.Canvas(graph_frame, height=449, width=600, )
sec_graph_frame.grid(column=0, row=0, columnspan=3)

gr_canvas = tk.Canvas(sec_graph_frame, height=400, width=600, bg="#cfcfcf")
gr_canvas.grid(column=0, row=0, columnspan=3)
gr_canvas.create_text(300, 200, fill="darkblue", font="Arial 25 italic bold", text=" Graph Area ")

tool_canvas = tk.Canvas(sec_graph_frame, height=45, width=600, bg="#cfcfcf")
tool_canvas.grid(column=0, row=1, columnspan=3)
tool_canvas.create_text(300, 25, fill="darkblue", font="Arial 15 italic bold", text=" ToolBar Area ")

# =============================| Info-box |=============================#
widget_func('label', graph_frame, 'Info-box', None, None, None, None, 0, 2, 6, 0, 1, 1, 'w')

infobox = scrolledtext.ScrolledText(graph_frame, width=72, height=6, wrap=tk.WORD)
infobox.grid(column=0, row=3, columnspan=3)

# ==================| Plotting Parameters Frame |==================#
plotting = ttk.LabelFrame(tab_1, text=' Plotting ')
plotting.grid(column=4, row=0, rowspan=2, padx=8, pady=4, sticky=tk.E)

# ============================| Graph Name |============================#
widget_func('label', plotting, 'Graph Name', None, None, None, None, 1, 0, 0, 0, 1, 1, None)
grtitle = tk.StringVar(plotting, value="X vs Y")
graph_name_entered = ttk.Entry(plotting, width=12, textvariable=grtitle)
graph_name_entered.grid(column=1, row=1, pady=5)

# ============================| X-Label |============================#
widget_func('label', plotting, 'X-Label', None, None, None, None, 1, 2, 0, 0, 1, 1, None)
xlabel = tk.StringVar(plotting, value="<default>")
x_name_entered = ttk.Entry(plotting, width=12, textvariable=xlabel)
x_name_entered.grid(column=1, row=3, pady=5)

# ============================| Y-Label |============================#
widget_func('label', plotting, 'Y-Label', None, None, None, None, 1, 4, 0, 0, 1, 1, None)
ylabel = tk.StringVar(plotting, value="<default>")
y_name_entered = ttk.Entry(plotting, width=12, textvariable=ylabel)
y_name_entered.grid(column=1, row=5, pady=5)

# ============================| Legend |============================#
widget_func('label', plotting, 'Legend', None, None, None, None, 1, 6, 0, 0, 1, 1, None)
grlegend = tk.StringVar(plotting, value="main curve")
legend_name_entered = ttk.Entry(plotting, width=12, textvariable=grlegend)
legend_name_entered.grid(column=1, row=7, pady=5)

# ==============================| Line thick |==============================#
widget_func('label', plotting, 'Line Thickness', None, None, None, None, 1, 8, 0, 0, 1, 1, None)
line_thik = Spinbox(plotting, values=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), width=10, bd=2, relief=tk.RAISED)
line_thik.grid(column=1, row=9, pady=5)
lt = line_thik.get()

# ========================-| Line color Dropdown |========================#
widget_func('label', plotting, 'Line Colour', None, None, None, None, 1, 10, 0, 0, 1, 1, None)
color_ = tk.StringVar()
color_chosen = ttk.Combobox(plotting, width=9, textvariable=color_, state='readonly')
color_chosen['values'] = (
    'Red', 'Blue', 'Green', 'Cyan', 'Magenta', 'Orange', 'Yellow', 'Olive', 'Gray', 'Purple', 'Brown', 'Black')
color_chosen.grid(column=1, row=11, pady=5)
color_chosen.current(0)

# ================| Graph Grid |================#
grid_ = ttk.LabelFrame(plotting, text=' Grid ')
grid_.grid(column=1, row=13, padx=6, )
radVar = tk.IntVar()
radVar.set(0)
curRad = tk.Radiobutton(grid_, text="On", variable=radVar, value=1, ).grid(column=1, row=14, )
curRad2 = tk.Radiobutton(grid_, text="Off", variable=radVar, value=0, ).grid(column=1, row=15, )

# ==========================| Button Area |==========================#
widget_func('btn', plotting, 'Add', None, None, None, openFile, 1, 16, 10, 0, 1, 1, None)  # Add btn
widget_func('btn', plotting, 'Plot', None, None, None, plotGraph, 1, 17, 1, 0, 1, 1, None)  # Plot btn
widget_func('btn', plotting, 'Refresh', None, None, None, re_fresh, 1, 18, 10, 0, 1, 1, None)  # Refresh btn
widget_func('btn', plotting, 'Close', None, None, None, _quit, 1, 19, 1, 0, 1, 1, None)  # Close btn


# =============| Program Icon |=============#
root.iconbitmap('gicon.ico')

root.mainloop()
