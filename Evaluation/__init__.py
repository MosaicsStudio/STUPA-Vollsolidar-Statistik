
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

# Filter out all incomplete responses (G03Q01 is not None)
DF_COMPLETED = G03Q01.answered(DF)

# Filter out all participants that didn´t spend at least 5s on the G03 page
DF_COMPLETED = G03.time.filter_numeric(
    DF_COMPLETED,
    lambda x: x >= 5
)

# Filter out all non-Students (G01Q01==AO01 => Student)
DF_FILTERED = G01Q01.of_answer(DF_COMPLETED, 'AO01')

print(f'Filtered DF with shape: {DF_FILTERED.shape}')

# ========================
# Evaluate the Data
# ========================

# Role Distribution (Pie)
with SaveFig('RoleDistribution', 'Actual Distribution of Roles in our Survey') as fig:
    G01Q01.pie_plot(DF, fig=fig, colors=MAIN_COLOR_PALETTE)

# Faculty Distribution (Pie)
with SaveFig('FacultyDistribution', 'Actual Distribution to Faculties in our Survey') as fig:
    DF_KNOWN_FACULTIES = G01Q02.of_answer(DF_FILTERED, ['AO01', 'AO02', 'AO03', 'AO04', 'AO05'])

    G01Q02.pie_plot(DF_KNOWN_FACULTIES, fig=fig, colors=FACULTIES_COLOR_PALETTE[1:], colors_mapped=COLOR_PALETTE_MAPPED, startangle=90)

OPT_DIST = {
    'ESB': 0.414,
    'INF': 0.206,
    'TEC': 0.170,
    'LS':  0.096,
    'TEX': 0.071,
}

# Optimum Faculty Distribution (Pie; Manually created)
with SaveFig('OptimumFacultyDistribution', 'Optimal Distribution') as fig:
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
with SaveFig('AgeDistribution', 'Age Distribution') as fig:
    G01Q04.pie_plot(DF_FILTERED, fig=fig, colors=MAIN_COLOR_PALETTE)

# Modes of Transport (Pie, Merged)
with SaveFig('ModesOfTransport', 'Modes of Transport (merged)') as fig:
    G04Q01.pie_plot(DF_FILTERED, fig=fig, colors=MAIN_COLOR_PALETTE)

# Distance vs. Time (With Category G04Q01)
with SaveFig('DistanceVsTime', 'Distance against Time by Modes of Transportation') as fig:
    G04Q05.against(
        G04Q06
    ).scatter_with_category(
        DF_FILTERED,
        fig=fig,
        category=G04Q01,
        x_log=True,
        colors=MAIN_COLOR_PALETTE,
        show_regression=True
    )

# Support Pie Chart
with SaveFig('SupportDTFSM', 'Support of the D-Ticket in the FSM') as fig:
    G03Q01.pie_plot(G03Q01.answered(DF_FILTERED), fig=fig, colors=MAIN_COLOR_PALETTE)

# Amount Reasonable?
with SaveFig('AmountReasonable', 'Is the proposed amount reasonable?') as fig:
    G06Q01.pie_plot(G06Q01.answered(DF_FILTERED), fig=fig, colors=MAIN_COLOR_PALETTE)

# Amounts considered reasonable by the students
with SaveFig('AmountsConsideredReasonable', 'Amounts considered reasonable by the students') as fig:
    G06Q02.histogram(G06Q02.answered(DF_FILTERED), fig=fig, bins=20, color=MAIN_COLOR_PALETTE[0])

# Fairness (Pie)
with SaveFig('Fairness', 'Is the proposed model fair?') as fig:
    G06Q03.pie_plot(G06Q03.answered(DF_FILTERED), fig=fig, colors=MAIN_COLOR_PALETTE)

# ========================
# Misc.
# ========================

# Get the actual percentages per faculty
FACULTY_PERCENTAGES = DF_FILTERED[G01Q02.code].value_counts(normalize=True)

# Remove -oth-
FACULTY_PERCENTAGES = FACULTY_PERCENTAGES.drop('-oth-')

# Map the faculty codes to the actual faculty names from the question
FACULTY_PERCENTAGES.index = FACULTY_PERCENTAGES.index.map(G01Q02.text_of_option)

# Subtract the optimal distribution from the actual distribution
FACULTY_DIFF = FACULTY_PERCENTAGES - pd.Series(OPT_DIST)

# Sort the series as in:
# INF, LS, ESB, TEC, TEX
FACULTY_DIFF = FACULTY_DIFF.reindex(['INF', 'LS', 'ESB', 'TEC', 'TEX'])

# Plot as a bar chart
with SaveFig('FacultyDifference', 'Difference between Actual and Optimal Faculty Distribution') as fig:
    ax = fig.gca()

    ax.bar(FACULTY_DIFF.index, FACULTY_DIFF.values, color=FACULTIES_COLOR_PALETTE[1:])

    ax.set_ylabel('Difference in %')
    ax.set_title('Difference between Actual and Optimal Faculty Distribution')

    for i, v in enumerate(FACULTY_DIFF):
        ax.text(i, v + 0.01, f'{v:.1%}', ha='center', va='bottom')

    # Y-Axis in percentage
    ax.yaxis.set_major_formatter('{x:.0%}')

    # Add x-Axis/Line at 0
    ax.axhline(0, color='black', linewidth=0.8)

    # Add vertical padding for bars
    ax.margins(y=0.2)

# ========================
# Auto TeX
# ========================

# Write the ParticipationText.tex
STUDENTS_TOTAL = 5_000

with open('Build/TeX/ParticipationText.tex', 'w') as f:
    f.write(f"""% TEX root = ../../Main.tex
We initiated a total of {DF.shape[0]} surveys, out of which {DF_COMPLETED.shape[0]} were fully completed.
This resulted in data from {DF_FILTERED.shape[0]} students, corresponding to around {(DF_FILTERED.shape[0] / STUDENTS_TOTAL) * 100:.0f}\% of the total student population on the main campus (approximately {STUDENTS_TOTAL} students).
Since this survey focuses on students, all subsequent graphs will exclusively use data from the student group.
""")
    
# Reasonable Amounts
G06Q02.make_numeric(DF_FILTERED)

BETWEEN_0_8 = DF_FILTERED[G06Q02.code].between(0, 8).sum()
BETWEEN_96_104 = DF_FILTERED[G06Q02.code].between(96, 104).sum()

with open('Build/TeX/AmountsConsideredReasonable.tex', 'w') as f:
    f.write(f"""% TEX root = ../../Main.tex
Since the pricing structure is of particular interest, participants who disagreed with G06Q1 (30\\%, \\ref{{fig:AmountReasonable}}) were given the option to propose their own pricing.
\\ref{{fig:AmountsConsideredReasonable}} visualizes these suggested price points, grouped by bins of 8 Euros. Interestingly, the most frequently suggested price points were 0 Euros and 100 Euros, with {BETWEEN_0_8} participants selecting the 0-8 Euro range and {BETWEEN_96_104} participants selecting the 96-104 Euro range. This may indicate that 
""")
    
# Fairness
VERY_UNFAIR = DF_FILTERED[G06Q03.code].value_counts(normalize=True).get('AO01', 0) * 100

with open('Build/TeX/Fairness.tex', 'w') as f:
    f.write(f"""% TEX root = ../../Main.tex
Interestingly whilst 70\\% of participants thought the amount was appropriate and around 80\% supported the \\acrshort{{dt}} in the \\acrshort{{fsm}} more than half of all participants answering this question thought the concept was unfair with {VERY_UNFAIR:.0f}\\% deeming it very unfair.
""")
