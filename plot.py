#!/usr/bin/env python
# coding: utf-8

# In[8]:


import matplotlib.pyplot as plt
import matplotlib.cm as mcm
import matplotlib.lines as mlines
import matplotlib.colors as mcolors
import atlas_mpl_style
import colorsys
import numpy as np
atlas_mpl_style.use_atlas_style(fancyLegend=True)


# In[9]:


################################################################
###                          INPUTS                          ###
###                                                          ###
### Edit the `vals` and `styles` variables with your data    ###
### and configuration                                        ###
###                                                          ###
################################################################

# A dictionary of group:data, with each entry corresponding to a group of bars
# in top to bottom order. The group name is shown on the y-label. `data` should be
# a dictionary containing entries collider:[limit, reference], in top to bottom
# order. It can also have optional entries 
#       - 'annotation': An annotation is added to the group label
#       - 'current limits': A value for the current limit, which is drawn as a vertical bar
vals = {
    'Massless Neutralino': {
        'HL-LHC': [1.7, 'Extrapolation'],
        'FCC-hh': [10.8, 'CERN-TH-2016-111'],
        'CLIC': [1.5, 'Private communication\n(ES Report)'],
        'annotation': r'$m(\tilde{chi_1^0})=0$',
        'current limits': 1.76,
    },
    'Compressed': {
        'HL-LHC': [0.85, 'Extrapolation'],
        'FCC-hh': [10, 'CERN-TH-2016-111'],
        'CLIC': [1.5, 'Private communication\n(ES Report)'],
        'annotation': r'add notation',
        'current limits': 0,
    },
}


# A dictionary of collider:styles, where the colliders correspond to those
# in `vals`. The order here is the order they appear in the legend. Styles 
# is a dictionary of options to Axes.barh. You can optionally also include 
# a style option 'annotation':annotation, which will append the annotation 
# to the legend description. 
# 
# Note that an option, if used, must be specified for all colliders. 
#
# https://matplotlib.org/3.5.0/api/_as_gen/matplotlib.axes.Axes.barh.html
cmap = mcm.get_cmap('Set3')
styles = {
    'HL-LHC': {'annotation':'14 TeV, 3 ab$^{-1}$', 'color':cmap(0), 'hatch':None},
    'FCC-hh': {'annotation':'100 TeV, 30 ab$^{-1}$', 'color':cmap(7), 'hatch':'/'},
    'ILC': {'annotation':'0.5 TeV, 4 ab$^{-1}$', 'color':cmap(3), 'hatch':'-'},
    'CLIC': {'annotation':'3 TeV, 5 ab$^{-1}$', 'color':cmap(4), 'hatch':'|'},
    'FCC-ee': {'annotation':'0.35 TeV, 12.6 ab$^{-1}$', 'color':cmap(2), 'hatch':'+'},
    'CEPC': {'annotation':'0.24 TeV, 10 ab$^{-1}$', 'color':cmap(5), 'hatch':'x'},
}


# In[11]:


################################################################
###                           PLOT                           ###
###                                                          ###
### You hopefully don't need to edit this block, but further ###
### customization can be hardcoded here.                     ###
###                                                          ###
################################################################

fig, ax = plt.subplots()
fig.set_dpi(144)

bar_height = 1 # height of a bar in data coordinates (keep this at 1)
group_pad = 0.5 # space between groups in data coordinates

# y-groups (search method)
labels = [] # string labels for each group
label_ys = [] # y position of the labels
dividers = [] # y positions of where to draw dividers between the groups
curr_lims = [] # (x, y0, y1) positions of the current limits

# bars
ys = [] # y position of each bar (lower edge)
widths = [] # width of each bar
references = [] # string reference of each bar
opts = {} # option : list per bar

# legend
legend_indexes = {} # collider : index into bars.patches

# Collate info. Loop from top to bottom (y-axis will be inverted, so start at y=0 and go up).
y = 0
for i,(group,colliders) in enumerate(vals.items()):
    y_group_start = y
    for collider,limits in colliders.items():
        if collider in ['annotation', 'current limits']:
            continue
        widths.append(limits[0])
        references.append(limits[1])
        ys.append(y)
        for opt,opt_val in styles[collider].items():
            if opt != 'annotation':
                opts.setdefault(opt, []).append(opt_val)
        legend_indexes.setdefault(collider, len(ys) - 1)
        y += bar_height
    if annotation := colliders.get('annotation'):
        group += '\n' + annotation
    labels.append(group)
    label_ys.append((y + y_group_start) / 2)
    dividers.append(y + group_pad / 2)
    if lim := colliders.get('current limits'):
        curr_lims.append((lim, 0 if len(dividers) < 2 else dividers[-2], y if i == len(vals) - 1 else dividers[-1]))
    y += group_pad
dividers = dividers[:-1] # don't draw a divider after the last group

# Auto-set hatch color
def darken(c, value=3):
    rgba = mcolors.to_rgba(c)
    h,l,s = colorsys.rgb_to_hls(*rgba[:3])
    new_rgb = colorsys.hls_to_rgb(h, min(1, l/value), s)
    return [*new_rgb, rgba[3]]
if 'color' in opts and 'hatch' in opts and 'edgecolor' not in opts:
    opts['edgecolor'] = [darken(c) for c in opts['color']]

# Plot main bars
bars = ax.barh(ys, widths, height=bar_height, align='edge', **opts)
ax.set_yticks(label_ys, labels)
ax.tick_params(axis='y', which='minor', left=False, right=False)
ax.set_ylim(0, ys[-1] + bar_height)
ax.invert_yaxis()
atlas_mpl_style.set_xlabel("Mass Reach [TeV]")
atlas_mpl_style.set_ylabel("Search Method")

# Plot current limits
for x,y0,y1 in curr_lims:
    lim_line = ax.plot([x, x], [y0, y1], linestyle='-', linewidth=3, color='#333333')

# Plot references and get x extent
x0,x1 = ax.get_xlim()
max_text_x = 0 # in axes coordinates
for y,ref in zip(ys, references):
    t = ax.text(x1 + 3, y + bar_height/2, ref, va='center', ha='center')
    bb = t.get_window_extent(renderer=fig.canvas.get_renderer()).transformed(ax.transAxes.inverted())
    max_text_x = max(max_text_x, bb.x1)
    # https://stackoverflow.com/questions/24581194/matplotlib-text-bounding-box-dimensions

# Plot dividers 
data_to_fig = ax.transAxes.inverted()
for y in dividers:
    ax.axhline(y, xmax=max_text_x + 0.02, linestyle='--', color='#666666', clip_on=False)

# Plot legend
legend_patches = [lim_line[0]]
legend_labels = ['LHC Limits']
for collider,opts in styles.items():
    if (index := legend_indexes.get(collider)) is not None:
        legend_patches.append(bars.patches[index])
        if annotation := opts.get('annotation'):
            collider += ' ' + annotation
        legend_labels.append(collider)
legend = ax.legend(legend_patches, legend_labels, framealpha=1, edgecolor='white', handleheight=1.4)


# In[ ]:



