
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import all modules; Load all python files that dont start with an underscore.
"""

import os
import importlib

from .Data import *
from .Classes import SaveFig

# ========================
# Import all modules
# ========================

# Load all python files that dont start with an underscore
files = os.listdir(os.path.dirname(__file__))

# Filter the files that dont start with an underscore
files = [file for file in files if not file.startswith('_') and file.endswith('.py')]

# Import all modules
for file in files:
    importlib.import_module(f'.{file[:-3]}', package=__name__)

# ========================
# Filter the DataFrame
# ========================

print(f'Got DF with shape: {DF.shape}')

# Filter out all non-Students (G01Q01==AO01 => Student)
DF = G01Q01.of_answer(DF, 'AO01')

# Filter out all incomplete responses (G03Q01 is not None)
DF = G03Q01.answered(DF)

# Filter out all participants that didn´t spend at least 5s on the G03 page
DF = G03.time.filter_numeric(
    DF,
    lambda x: x >= 5
)

print(f'Filtered DF with shape: {DF.shape}')

# ========================
# Evaluate the Data
# ========================

# Faculty Distribution (Pie)
with SaveFig('FacultyDistribution') as fig:
    DF_KNOWN_FACULTIES = G01Q02.of_answer(DF, ['AO01', 'AO02', 'AO03', 'AO04', 'AO05'])

    G01Q02.pie_plot(DF_KNOWN_FACULTIES, fig=fig, colors=FACULTIES_COLOR_PALETTE[1:], colors_mapped=COLOR_PALETTE_MAPPED, startangle=90)

# Optimum Faculty Distribution (Pie; Manually created)
with SaveFig('OptimumFacultyDistribution') as fig:
    OPT_DIST = {
        'ESB': 0.414,
        'INF': 0.206,
        'TEC': 0.170,
        'LS':  0.096,
        'TEX': 0.071,
    }

    PAIRS = [(key, value) for key, value in OPT_DIST.items()]

    # Sort like in FACULTIES_COLOR_PALETTE[1:]
    PAIRS = sorted(PAIRS, key=lambda x: FACULTIES_COLOR_PALETTE[1:].index(COLOR_PALETTE_MAPPED[x[0]]))

    KEYS = [pair[0] for pair in PAIRS]
    VALUES = [pair[1] for pair in PAIRS]

    ax = fig.gca()

    ax.pie(VALUES, startangle=90, labels=KEYS, autopct='%1.1f%%', colors=FACULTIES_COLOR_PALETTE[1:])

    ax.title.set_text('Optimal Faculty Distribution')

    labels_groups = [node for node in ax.texts if '%' not in node.get_text()]

    for label in labels_groups:
        label_text = label.get_text()

        if '%' in label_text:
            foreground = 'white'
            background = 'black'
        else:
            foreground = 'black'
            background = 'white'

            if label_text in COLOR_PALETTE_MAPPED:
                foreground = COLOR_PALETTE_MAPPED[label_text]

        label.set_fontsize(12)
        label.set_fontweight('bold')
        label.set_bbox(dict(facecolor=background, alpha=0.5, edgecolor=foreground, boxstyle='round,pad=0.2'))
        label.set_color(foreground)

# Age Distribution (Pie)
with SaveFig('AgeDistribution') as fig:
    G01Q04.pie_plot(DF, fig=fig, colors=MAIN_COLOR_PALETTE)

# Modes of Transport (Pie, Merged)
with SaveFig('ModesOfTransport') as fig:
    G04Q01.pie_plot(DF, fig=fig, colors=MAIN_COLOR_PALETTE)

# Distance vs. Time (With Category G04Q01)
with SaveFig('DistanceVsTime') as fig:
    G04Q05.against(
        G04Q06
    ).scatter_with_category(
        DF,
        fig=fig,
        category=G04Q01,
        x_log=True,
        colors=MAIN_COLOR_PALETTE,
        show_regression=True
    )