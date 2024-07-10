#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Save figures to the Output/Images folder.
"""

import os
from matplotlib.figure import Figure

class SaveFig(Figure):
    def __init__(self, filename: str, folder: str='Build/Images'):
        assert '/' not in filename, f"Invalid filename: {filename}"

        self.filename = os.path.join(folder, filename)
        super().__init__()

    def __enter__(self):
        print(f'\x1b[1;32m[INFO]\x1b[0m Making {self.filename}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not os.path.exists(os.path.dirname(self.filename)):
            os.makedirs(os.path.dirname(self.filename))

        format = self.filename.split('.')[-1]
    
        if self.filename.count('.') == 0 or format not in ['png', 'jpg', 'jpeg', 'pdf', 'svg']:
            format = 'svg'
            self.filename += '.svg'

        self.savefig(self.filename, format=format)