#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get latest file in ths folder, that ends with .json, load it and create a DataFrame.
"""


import json
import os

import pandas as pd
import matplotlib.pyplot as plt

from .Questions import *

DF: pd.DataFrame = None

# Load the survey results
EVAL_FOLDER = os.path.dirname(__file__)

# Get the latest survey results file
files = os.listdir(EVAL_FOLDER)

# Filter the files that end with .json
files = [os.path.join(EVAL_FOLDER, file) for file in files if file.endswith('.json')]

if not files:
    raise FileNotFoundError(f"No JSON files found in {EVAL_FOLDER}")
else:
    # Get the latest file
    latest_file = max(files, key=os.path.getctime)

    with open(latest_file, 'r') as f:
        survey_results = json.load(f)

    # Create a DataFrame from the survey results
    DF = pd.DataFrame(survey_results['responses'])


# Constants
## Color Palettes
MAIN_COLOR_PALETTE = [
    '#EE6352',
    '#E4B7E5',
    '#58A4B0',
    '#484D6D',
    '#FFFC99',
    '#48ACF0'
]

FACULTIES_COLOR_PALETTE = [
    '#707173',
    '#FFCC00',
    '#F08A00',
    '#13235B',
    '#0076BD',
    '#CD0529'
]

COLOR_PALETTE_MAPPED = {
    'INF': FACULTIES_COLOR_PALETTE[1],
    'LS': FACULTIES_COLOR_PALETTE[2],
    'ESB': FACULTIES_COLOR_PALETTE[3],
    'TEC': FACULTIES_COLOR_PALETTE[4],
    'TEX': FACULTIES_COLOR_PALETTE[5]
}
