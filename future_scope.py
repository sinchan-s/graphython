import random
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import messagebox as msg
from tkinter import ttk, Menu, Spinbox, filedialog, scrolledtext
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import lmfit.models as mdl

# =============|  Import Button function |=============#
def importGraph():
    infobox.insert(tk.INSERT, "\nGraph imported for Curve-Fitting\n")
    p_fig = (7, 3.5)
    cc_ = 'k'
    sourceGraph(p_fig, cc_, gr_canvas2, tool_canvas2)


# =============| Apply Button function |=============#
def applyBtn():
    p_fig = (7, 3.5)
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
    sourceGraph(p_fig, cc_, gr_canvas2, tool_canvas2, x_min=xMin, x_max=xMax)
    return xMin, xMax


# ============| Generate deconvolution function |============#
def generate_model(spec):
    try:
        selected_range = csvDf[(x_col > (xMin - 1)) & (x_col < xMax + 1)]
        global x, y, params
        x = selected_range.x_val
        y = selected_range.y_val
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


tab_2 = ttk.Frame(tabControl)
tabControl.add(tab_2, text=' Curve-fit ')
tab_3 = ttk.Frame(tabControl)
tabControl.add(tab_3, text=' Statistics ')

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
