
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

# Filter out all non-Students (G01Q01==AO01 => Student)
DF_FILTERED_STUDENT = G01Q01.of_answer(DF_COMPLETED, 'AO01')

# Filter out all participants that didn´t spend at least 5s on the G03 page
DF_FILTERED_TIME = G03.time.filter_numeric(
    DF_FILTERED_STUDENT,
    lambda x: x >= 15
)

# Filter out all above 26 that claim to have a student ticket G04Q07:(AO02, AO03) x G01Q04:Y (LIARS!)
DF_FILTERED = DF_FILTERED_TIME[
    ~(
        (DF_FILTERED_TIME[G04Q07.code].isin(['AO02', 'AO03'])) &
        (DF_FILTERED_TIME[G01Q04.code] == 'Y')
    )
]

print(f'Filtered DF with shape: {DF_FILTERED.shape}')

# ========================
# Evaluate the Data
# ========================

# Role Distribution (Pie)
with SaveFig('RoleDistribution', 'Actual Distribution of Roles in our Survey') as fig:
    G01Q01.pie_plot(DF, fig=fig, colors=MAIN_COLOR_PALETTE)

# Faculty Distribution (Pie)
with SaveFig('FacultyDistribution', 'Actual Distribution to Faculties in our Survey') as fig:
    DF_KNOWN_FACULTIES = G01Q02.of_answer(DF_FILTERED_STUDENT, ['AO01', 'AO02', 'AO03', 'AO04', 'AO05'])

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

    previous_label = None

    for label in ax.texts:
        label_text: str = label.get_text()

        foreground = 'black'
        background = 'white'

        if label_text in COLOR_PALETTE_MAPPED:
            foreground = COLOR_PALETTE_MAPPED[label_text]

        label.set_fontsize(10)
        label.set_fontweight('bold')
        label.set_bbox(dict(facecolor=background, alpha=0.5, edgecolor=foreground, boxstyle='round,pad=0.2'))
        label.set_color(foreground)

        previous_label = label_text

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

# Modes of transport by faculty
with SaveFig('ModesOfTransportByFaculty', 'Modes of Transport by Faculty') as fig:
    G01Q02.against(G04Q01).bar_options_plot(
        fig,
        DF_FILTERED,
        title='Modes of Transport by Faculty',
        color_palette=MAIN_COLOR_PALETTE,
        custom_x_text='Faculty',
        custom_y_text='Share',
        normalize=True,
        color_palette_mapped=COLOR_PALETTE_MAPPED
    )

# Modes of Transport against distance - bins of 5km
with SaveFig('ModesOfTransportAgainstDistance', 'Modes of Transport against Distance') as fig:
    DF_BINNED, G04Q05_BINNED = G04Q05.numeric_to_bins_options(DF_FILTERED, 10, max=50)

    G04Q05_BINNED.against(G04Q01).bar_options_plot(
        fig,
        DF_BINNED,
        title='Modes of Transport against Distance (Merged)',
        color_palette=MAIN_COLOR_PALETTE,
        custom_x_text='Distance (in km)',
        custom_y_text='Share',
        normalize=True
    )

# Importance of climate friendliness in transport decisions vs. modes of transport
with SaveFig('ClimateFriendlinessImportanceVsTransport', 'Importance of climate friendliness in transport decisions vs. modes of transport') as fig:
    G07Q01.against(G04Q01).bar_options_plot(
        fig,
        DF_FILTERED,
        title='Importance of climate friendliness in transport decisions vs. modes of transport',
        color_palette=MAIN_COLOR_PALETTE,
        custom_x_text='Importance of climate friendliness in transport decisions',
        custom_y_text='Share of modes of transport',
        normalize=True
    )

# Expected impact of having a Deutschlandticket on your mode of transportation
with SaveFig('ExpectedImpact', 'Would you expect an impact on your usage of\npublic transportation if you got a D-Ticket?') as fig:
    G07Q01.pie_plot(G07Q01.answered(DF_FILTERED), fig=fig, colors=MAIN_COLOR_PALETTE)

# Perception on fairness against modes of transport
with SaveFig('FairnessVsTransport', 'Perception on fairness against modes of transport') as fig:
    G06Q03.against(G04Q01).bar_options_plot(
        fig,
        DF_FILTERED,
        title='Perception on fairness against modes of transport',
        color_palette=MAIN_COLOR_PALETTE,
        custom_x_text='Perception on fairness',
        custom_y_text='Share of modes of transport',
        normalize=True
    )

# Support against modes of transport
with SaveFig('SupportVsTransport', 'Support against modes of transport') as fig:
    G03Q01.against(G04Q01).bar_options_plot(
        fig,
        DF_FILTERED,
        title='Support against modes of transport',
        color_palette=MAIN_COLOR_PALETTE,
        custom_x_text='Support',
        custom_y_text='Share of modes of transport',
        normalize=True
    )

# Support against Faculty
with SaveFig('SupportVsFaculty', 'Support against Faculty') as fig:
    G03Q01.against(G01Q02).bar_options_plot(
        fig,
        DF_FILTERED_STUDENT,
        title='Support against Faculty',
        color_palette=FACULTIES_COLOR_PALETTE,
        custom_x_text='Support',
        custom_y_text='Share of Faculty',
        normalize=True,
        color_palette_mapped=COLOR_PALETTE_MAPPED
    )

# ========================
# Misc.
# ========================

# Get the actual percentages per faculty
FACULTY_PERCENTAGES = DF_FILTERED_STUDENT[G01Q02.code].value_counts(normalize=True)

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

    ax.set_ylabel('Deviation in % of total students')
    ax.set_title('Difference between Actual and Optimal Faculty Distribution')

    for i, v in enumerate(FACULTY_DIFF):
        label = ax.text(i, v + 0.01, f'{v:.1%}', ha='center', va='bottom')

        foreground = COLOR_PALETTE_MAPPED[FACULTY_DIFF.index[i]]
        background = 'white'

        label.set_fontsize(10)
        label.set_fontweight('bold')
        label.set_bbox(dict(facecolor=background, alpha=0.5, edgecolor=background, boxstyle='round,pad=0.2'))
        label.set_color(foreground)

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
Since this survey focuses on students, all subsequent graphs will exclusively use data from the student group.
This resulted in data from {DF_FILTERED_STUDENT.shape[0]} students, corresponding to around {(DF_FILTERED.shape[0] / STUDENTS_TOTAL) * 100:.0f}\% of the total student population on the main campus (approximately {STUDENTS_TOTAL} students).
These were further filtered to exclude participants who spent less than 15 seconds on the information page. Furthermore, we excluded participants who claimed to have a student ticket but were above the age of 26. This yielded a final dataset of {DF_FILTERED.shape[0]} students.
""")
    
# Reasonable Amounts
G06Q02.make_numeric(DF_FILTERED)

BETWEEN_0_8 = DF_FILTERED[G06Q02.code].between(0, 8).sum()
BETWEEN_96_104 = DF_FILTERED[G06Q02.code].between(96, 104).sum()

with open('Build/TeX/AmountsConsideredReasonable.tex', 'w') as f:
    f.write(f"""% TEX root = ../../Main.tex
Since the pricing structure is of particular interest, participants who disagreed with G06Q1 (30\\%, \\ref{{fig:AmountReasonable}}) were given the option to propose their own pricing.
\\ref{{fig:AmountsConsideredReasonable}} visualizes these suggested price points, grouped by bins of 8 Euros. Interestingly, the most frequently suggested price points were 0 Euros and 100 Euros, with {BETWEEN_0_8} participants selecting the 0-8 Euro range and {BETWEEN_96_104} participants selecting the 96-104 Euro range.
""")
    
# Fairness
VERY_UNFAIR = DF_FILTERED[G06Q03.code].value_counts(normalize=True).get('AO01', 0) * 100

with open('Build/TeX/Fairness.tex', 'w') as f:
    f.write(f"""% TEX root = ../../Main.tex
Interestingly whilst 70\\% of participants thought the amount was appropriate and around 80\% supported the \\gls{{dt}} in the \\gls{{fsm}} more than half of all participants answering this question thought the concept was unfair with {VERY_UNFAIR:.0f}\\% deeming it very unfair.
""")


# How often do these words appear in the last question (Free Text); Create Table in LaTeX
WORDS = {
    'For Free': ['umsonst', 'kostenlos', '0€', '0 €', '0 euro', 'null euro', 'free'],
    'Expensive': ['teuer', 'zu teuer', 'zu viel', 'expensive'],
    'Unfair': ['unfair', 'ungerecht', 'unfairness', 'unfairly'],
    'Partial Solidarity': ['selbst entscheiden', 'selbst kaufen', 'selbst kaufen', 'teil solidar', 'partial solidarity', 'teilsolidar'],
}

COUNTS = {key: 0 for key in WORDS.keys()}

for key, words in WORDS.items():
    COUNTS[key] = DF_FILTERED[
        DF_FILTERED[G08Q01.code].str.contains('|'.join(words), case=False, na=False)
    ].shape[0]

COUNTS_TUPLES_SORTED = sorted(COUNTS.items(), key=lambda x: x[1], reverse=True)

# Write the LaTeX Table
with open('Build/TeX/WordCountTable.tex', 'w') as f:
    f.write(f"""% TEX root = ../../Main.tex
\\begin{{table}}[H]
\\centering
\\begin{{tabular}}{{|l|c|}}
\\hline
Word Group & Count \\\\
\\hline
""")

    for key, value in COUNTS_TUPLES_SORTED:
        f.write(f'{key} & {value} \\\\\n')

    f.write("""\\hline
\\end{tabular}
\\caption{Counts per Word Group in the last question (Free Text)}
\\label{tab:WordCountTable}
\\end{table}
""")

## Groups used
with open('Build/TeX/WordCountGroupsTable.tex', 'w') as f:
    f.write(f"""% TEX root = ../../Main.tex
\\begin{{table}}[H]
\\centering
\\begin{{tabular}}{{|l|c|}}
\\hline
Word Group & Words \\\\
\\hline
""")

    for key, value in WORDS.items():
        f.write(f'{key} & {" \\\\\n & ".join(v.replace('€', '\\texttt{\\{euro\\}}') for v in value)} \\\\\n')

    f.write("""\\hline
\\end{tabular}
\\caption{Groups used in the Word Count Table}
\\label{tab:WordCountGroupsTable}
\\end{table}
""")