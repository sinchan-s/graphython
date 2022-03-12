import random
import tkinter as tk
from tkinter import messagebox as msg
from tkinter import ttk, Menu, Spinbox, filedialog, scrolledtext
import lmfit.models as mdl
import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

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
            csvDf = pd.read_csv(open(file_), names=['xval', 'yval'])
        global y_col
        y_col = csvDf.yval
        global x_col
        x_col = csvDf.xval
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
    pfig = (6, 4)
    cc_ = (color_chosen.get()).lower()
    sourceGraph(pfig, cc_, gr_canvas, tool_canvas)


# =============| Refresh Button function |=============#
def re_fresh():
    pfig = (6, 4)
    cc_ = (color_chosen.get()).lower()
    sec_graph_frame.destroy()
    gr_canvas = tk.Canvas(graph_frame, height=400, width=600, bg="#ffffff")
    gr_canvas.grid(column=0, row=0, columnspan=3)
    tool_canvas = tk.Canvas(graph_frame, height=45, width=600, bg="#cfcfcf")
    tool_canvas.grid(column=0, row=1, columnspan=3)
    info_call()
    sourceGraph(pfig, cc_, gr_canvas, tool_canvas)


# =============|  Import Button function |=============#
def importGraph():
    infobox.insert(tk.INSERT, "\nGraph imported for Curve-Fitting\n")
    pfig = (7, 3.5)
    cc_ = 'k'
    sourceGraph(pfig, cc_, gr_canvas2, tool_canvas2)


# =============| Apply Button function |=============#
def applyBtn():
    pfig = (7, 3.5)
    cc_ = 'k'
    global xMin
    xMin = int(range_from.get())
    global xMax
    xMax = int(range_to.get())
    sec_graph_frame2.destroy()
    gr_canvas2 = tk.Canvas(graph_frame2, height=350, width=700, bg="#ffffff")
    gr_canvas2.grid(column=0, row=0, columnspan=3)
    tool_canvas2 = tk.Canvas(graph_frame2, height=45, width=700, bg="#cfcfcf")
    tool_canvas2.grid(column=0, row=1, columnspan=3)
    info_call()
    sourceGraph(pfig, cc_, gr_canvas2, tool_canvas2, x_min=xMin, x_max=xMax)
    return xMin, xMax


# ============| Generate deconvolution function |============#
def generate_model(spec):
    try:
        selected_range = csvDf[(x_col > (xMin - 1)) & (x_col < xMax + 1)]
        global x, y, params
        x = selected_range.xval
        y = selected_range.yval
        composite_model = None
        params = None
        x_min = np.min(x)
        x_max = np.max(x)
        x_range = x_max - x_min
        y_min = np.min(y)
        y_max = np.max(y)
        for i, basis_func in enumerate(spec['model']):
            prefix = f'm{i}_'
            print(f'\nprefix:\n{prefix}\n')
            model = getattr(mdl, basis_func['type'])(prefix=prefix)
            print(f'\nmodel:\n{model}\n')
            if basis_func['type'] in ['GaussianModel', 'LorentzianModel', 'VoigtModel']:
                model.set_param_hint('sigma', min=0, max=x_range)
                model.set_param_hint('center', min=x_min, max=x_max)
                model.set_param_hint('height', min=0, max=y_max)
                model.set_param_hint('amplitude', min=0)
                default_params = {
                    prefix + 'center': x_min + x_range * random.random(),
                    prefix + 'height': y_max * random.random(),
                    prefix + 'sigma': x_range * random.random()
                }
                print(basis_func)
                print(f'\ndefault-params:\n{default_params}\n')
            else:
                raise NotImplemented(f'model {basis_func["type"]} not implemented yet')

            model_params = model.make_params(**default_params, **basis_func.get('params', {}))

            if params is None:
                params = default_params
            else:
                params.update(model_params)

            if composite_model is None:
                composite_model = model
            else:
                composite_model = composite_model + model
        return composite_model, params
    except NameError:
        pass


# ===========| Deconvolute button function |===========#
def deconvolute():
    spec = {
        'model': [
            {'type': 'GaussianModel'},
            {'type': 'GaussianModel'}
        ]
    }

    try:
        model, params = generate_model(spec)
        output = model.fit(y, params, x=x)
        fig = output.plot_fit(data_kws={'markersize': 1})
        print(output.fit_report())
        plt.show()
    except TypeError:
        pass


# ==============| Set button function |==============#
def setPeaks():
    peak_count = int(peak_chosen.get())
    for i in range(peak_count):
        slider_v = ttk.Scale(deconvo_area, from_=1, to=10, orient=tk.VERTICAL)
        slider_v.grid(column=i + 1, row=5)
        slider_h = ttk.Scale(deconvo_area, from_=1, to=10, )
        slider_h.grid(column=i + 1, row=5)
    slider_v.destroy()
    slider_h.destroy()


# = GUI Callback function - Checkbox=#
def checkCallback(*ignoredArgs):
    # only enable one checkbutton
    if chVarUn.get():
        check3.configure(state='disabled')
    else:
        check3.configure(state='normal')
    if chVarEn.get():
        check2.configure(state='disabled')
    else:
        check2.configure(state='normal')


# ===========| Info-box ouput function |============#
def info_call():
    info = f'\n~Graph name: {grtitle.get()}\n~X-Label: {xlabel.get()}\n~Y-Label: {ylabel.get()}\n~Legend: {grlegend.get()}\n~Line Thickness: {line_thik.get()}\n~Line color: {color_chosen.get()}\n'
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


# ==============| Widgets func |==============#
''' wdgt('label', graph_frame, 'Info-box', None, None, None, None, 0, 2, 6, 0, 1, 1, 'w')
class getWidget:
    def __init__(self, widget, tabName, text_, textv, height, width, command, column, row, py, px, cs, rs, stik_, **kwargs):
        self.textv = textv
        self.stik_ = stik_
        self.tabname = tabname
'''
def wdgt(widget, tabName, text_, textv_, he_, wi_, command_, c_, r_, py_, px_, cs_, rs_, stik_, **kwargs):
    if widget == 'btn':
        ttk.Button(tabName, text=text_, command=command_).grid(column=c_, row=r_, pady=py_, padx=px_, columnspan=cs_,
                                                               rowspan=rs_, sticky=stik_)
    elif widget == 'label':
        ttk.Label(tabName, text=text_).grid(column=c_, row=r_, pady=py_, padx=px_, columnspan=cs_, rowspan=rs_,
                                            sticky=stik_)


# ======================================================================================#     ####   ####
# =======================                   Menu Area            =======================#    ##  |##|   ##
# ======================================================================================#   ##    ##     ##

# -------------------| Menu Bar |-------------------#
menu_bar = Menu(root)
root.config(menu=menu_bar)

# -------------------| File Menu |------------------#
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=openFile)
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
'''tab_2 = ttk.Frame(tabControl)
tabControl.add(tab_2, text=' Curve-fit ')
tab_3 = ttk.Frame(tabControl)
tabControl.add(tab_3, text=' Statistics ')'''
tabControl.pack(expand=1, fill="both")

########################################################################################		##
#####################                   Tab-1 Area            ##########################		##
########################################################################################		##

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
wdgt('label', graph_frame, 'Info-box', None, None, None, None, 0, 2, 6, 0, 1, 1, 'w')

infobox = scrolledtext.ScrolledText(graph_frame, width=72, height=6, wrap=tk.WORD)
infobox.grid(column=0, row=3, columnspan=3)

# ==================| Plotting Parameters Frame |==================#
plotting = ttk.LabelFrame(tab_1, text=' Plotting ')
plotting.grid(column=4, row=0, rowspan=2, padx=8, pady=4, sticky=tk.E)

# ============================| Graph Name |============================#
wdgt('label', plotting, 'Graph Name', None, None, None, None, 1, 0, 0, 0, 1, 1, None)
grtitle = tk.StringVar(plotting, value="X vs Y")
graph_name_entered = ttk.Entry(plotting, width=12, textvariable=grtitle)
graph_name_entered.grid(column=1, row=1, pady=5)

# ============================| X-Label |============================#
wdgt('label', plotting, 'X-Label', None, None, None, None, 1, 2, 0, 0, 1, 1, None)
xlabel = tk.StringVar(plotting, value="<default>")
x_name_entered = ttk.Entry(plotting, width=12, textvariable=xlabel)
x_name_entered.grid(column=1, row=3, pady=5)

# ============================| Y-Label |============================#
wdgt('label', plotting, 'Y-Label', None, None, None, None, 1, 4, 0, 0, 1, 1, None)
ylabel = tk.StringVar(plotting, value="<default>")
y_name_entered = ttk.Entry(plotting, width=12, textvariable=ylabel)
y_name_entered.grid(column=1, row=5, pady=5)

# ============================| Legend |============================#
wdgt('label', plotting, 'Legend', None, None, None, None, 1, 6, 0, 0, 1, 1, None)
grlegend = tk.StringVar(plotting, value="main curve")
legend_name_entered = ttk.Entry(plotting, width=12, textvariable=grlegend)
legend_name_entered.grid(column=1, row=7, pady=5)

# ==============================| Line thick |==============================#
wdgt('label', plotting, 'Line Thickness', None, None, None, None, 1, 8, 0, 0, 1, 1, None)
line_thik = Spinbox(plotting, values=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), width=10, bd=2, relief=tk.RAISED)
line_thik.grid(column=1, row=9, pady=5)
lt = line_thik.get()

# ========================-| Line color Dropdown |========================#
wdgt('label', plotting, 'Line Colour', None, None, None, None, 1, 10, 0, 0, 1, 1, None)
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
curRad = tk.Radiobutton(grid_, text="Off", variable=radVar, value=0, ).grid(column=1, row=15, )

# ==========================| Button Area |==========================#
wdgt('btn', plotting, 'Add', None, None, None, openFile, 1, 16, 10, 0, 1, 1, None)  # Add btn
wdgt('btn', plotting, 'Plot', None, None, None, plotGraph, 1, 17, 1, 0, 1, 1, None)  # Plot btn
wdgt('btn', plotting, 'Apply', None, None, None, re_fresh, 1, 18, 10, 0, 1, 1, None)  # Apply btn
wdgt('btn', plotting, 'Close', None, None, None, _quit, 1, 19, 1, 0, 1, 1, None)  # Close btn

'''
# ======================================================================================#		##  ##
# ====================                   Tab-2 Area                 ====================#		##  ##
# ======================================================================================#		##  ##

# =====================| Graph Canvas2 Frame|=====================#
graph_frame2 = ttk.LabelFrame(tab_2, text=' Curve Fitting Area ')
graph_frame2.grid(column=0, row=0, columnspan=11, padx=8, pady=4)
sec_graph_frame2 = tk.Canvas(graph_frame2, height=399, width=700, bg="#cfcfcf")
sec_graph_frame2.grid(column=0, row=0, columnspan=11)

gr_canvas2 = tk.Canvas(sec_graph_frame2, height=350, width=700, bg="#cfcfcf")
gr_canvas2.grid(column=0, row=0, columnspan=11)
gr_canvas2.create_text(350, 175, fill="darkblue", font="Arial 25 italic bold", text=" Import graph for deconvolution ")
tool_canvas2 = tk.Canvas(sec_graph_frame2, height=45, width=700, bg="#cfcfcf")
tool_canvas2.grid(column=0, row=1, columnspan=11)
tool_canvas2.create_text(350, 25, fill="darkblue", font="Arial 15 italic bold", text=" ToolBar Area ")

# ===================| Deconvo Parameters Frame |===================#
deconvo_area = ttk.LabelFrame(tab_2, text=' Curve Deconvolution ')
deconvo_area.grid(column=0, row=2, columnspan=11, rowspan=4, padx=8, pady=4, sticky=tk.W)
wdgt('btn', deconvo_area, 'Import Graph', None, None, None, importGraph, 0, 4, 0, 5, 1, 1, 'w')  # Import btn
wdgt('btn', deconvo_area, 'Deconvolute', None, None, None, deconvolute, 3, 4, 0, 5, 1, 1, 'e')  # Deconvo btn
wdgt('label', deconvo_area, 'No. of Peaks', None, None, None, None, 0, 5, 0, 5, 1, 1, 'w')  # Peaks label
peaks_ = tk.IntVar()
peak_chosen = ttk.Combobox(deconvo_area, width=9, textvariable=peaks_, state='readonly')  # Peak dropdown
peak_chosen['values'] = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
peak_chosen.grid(column=0, row=6, padx=5, pady=2, sticky='w')
peak_chosen.current(0)
wdgt('btn', deconvo_area, 'Set', None, None, None, setPeaks, 0, 7, 2, 5, 1, 1, 'w')  # Set btn

# ==========================| Range Entry |==========================#
range_frame = ttk.LabelFrame(deconvo_area, text=' Set Graph Range ')  # Range frame
range_frame.grid(column=0, row=8, columnspan=2, rowspan=2, pady=8)
wdgt('label', range_frame, 'From: ', None, None, None, None, 0, 9, 0, 5, 1, 1, None)  # From label
range_from_entry = tk.IntVar(range_frame, value="0")
range_from = ttk.Entry(range_frame, width=12, textvariable=range_from_entry)
range_from.grid(column=1, row=9, pady=5)
wdgt('label', range_frame, 'To: ', None, None, None, None, 2, 9, 0, 5, 1, 1, None)  # To label
range_to_entry = tk.IntVar(range_frame, value="0")
range_to = ttk.Entry(range_frame, width=12, textvariable=range_to_entry)
range_to.grid(column=3, row=9, pady=5)
wdgt('btn', deconvo_area, 'Apply', None, None, None, applyBtn, 3, 9, 0, 3, 1, 1, None)  # Apply btn


# Creating three checkbuttons
chVarDis = tk.IntVar()
check1 = tk.Checkbutton(graph_frame2, text="Disabled", variable=chVarDis, state='disabled')
check1.select()
check1.grid(column=0, row=4, sticky=tk.W)                   

chVarUn = tk.IntVar()
check2 = tk.Checkbutton(graph_frame2, text="UnChecked", variable=chVarUn)
check2.deselect()
check2.grid(column=1, row=4, sticky=tk.W)                   

chVarEn = tk.IntVar()
check3 = tk.Checkbutton(graph_frame2, text="Enabled", variable=chVarEn)
check3.deselect()
check3.grid(column=2, row=4, sticky=tk.W)                     

# trace the state of the two checkbuttons
chVarUn.trace('w', lambda unused0, unused1, unused2 : checkCallback())    
chVarEn.trace('w', lambda unused0, unused1, unused2 : checkCallback())   


# ======================================================================================#		##  ##  ##
# ====================                   Tab-3 Area                 ====================#		##  ##  ##
# ======================================================================================#		##  ##  ##

# =======================| Statistics Report |=======================#
graph_frame3 = ttk.LabelFrame(tab_3, text=' Curve Fitting report ')
graph_frame3.grid(column=0, row=0, padx=8, pady=4, columnspan=4, rowspan=5)
stat_box = scrolledtext.ScrolledText(graph_frame3, width=85, height=37, wrap=tk.WORD)
stat_box.grid(column=0, row=3, )
'''

# =============| Program Icon |=============#
root.iconbitmap('gicon.ico')


root.mainloop()
