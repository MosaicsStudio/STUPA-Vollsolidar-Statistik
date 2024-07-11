#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Save figures to the Output/Images folder.
"""

import inspect
import os
import sys
from matplotlib.figure import Figure

class SkipWithBlock(Exception):
    pass

class SaveFig(Figure):
    """
    Save figures to the Output/Images folder and create a tex file for the figure.
    """

    __folder_svg = 'Build/Images'
    __folder_tex = 'Build/TeX/Figures'

    __filename_svg: str
    __filename_tex: str
    
    __format: str

    __caption: str

    __basename: str

    @property
    def filename_svg(self):
        return self.__filename_svg

    @property
    def filename_tex(self):
        return self.__filename_tex
    
    @property
    def format(self):
        return self.__format
    
    @property
    def caption(self):
        return self.__caption
    
    @property
    def basename(self):
        return self.__basename

    def __init__(self, filename: str, caption: str='A Caption', folder_svg: str=None, folder_tex: str=None):
        assert '/' not in filename, f"Invalid filename: {filename}"

        self.__caption = caption

        if folder_svg is not None:
            self.__folder_svg = folder_svg

        if folder_tex is not None:
            self.__folder_tex = folder_tex

        self.__filename_svg = os.path.join(self.__folder_svg, filename)
        self.__filename_tex = os.path.join(self.__folder_tex, filename)

        self.__format = filename.split('.')[-1]
    
        if filename.count('.') == 0 or format not in ['png', 'jpg', 'jpeg', 'pdf', 'svg']:
            self.__format = 'svg'
            self.__filename_svg += '.svg'
            self.__filename_tex += '.tex'
        else:
            self.__filename_tex = filename.replace(self.format, 'tex')

        self.__basename = filename.replace(f'.{self.format}', '')

        super().__init__()

    def __enter__(self):
        print(f'\x1b[1;32m[INFO]\x1b[0m Making {self.basename}')
        if not self.has_changed():
            print(f'\x1b[1;32m[INFO]\x1b[0m {self.basename} is up to date.')
            # Do some magic
            sys.settrace(lambda *args, **keys: None)
            frame = sys._getframe(1)
            frame.f_trace = self.trace
        else:
            print(f'\x1b[1;33m[INFO]\x1b[0m {self.basename} is outdated.')
            return self
            
    def trace(self, frame, event, arg):
        raise SkipWithBlock()
    
    def has_changed(self):
        # Check if the TeX and SVG files exist
        if not os.path.exists(self.filename_tex) or not os.path.exists(self.filename_svg):
            return True

        # Get last change timestamp for Evaluation/Data/Questions/__init__.py
        last_change = os.path.getmtime('Evaluation/Data/Questions/__init__.py')

        # Get last change timestamp for Evaluation/Data/*.json
        last_change_json = max([
            os.path.getmtime(
                os.path.join('Evaluation/Data', file)
            )
            for file in os.listdir('Evaluation/Data') if file.endswith('.json')
        ])
    
        # Get Last Changes for the TeX and SVG files
        last_change_tex = os.path.getmtime(self.filename_tex)
        last_change_svg = os.path.getmtime(self.filename_svg)

        # Get Max of __init__.py and *.json
        last_change = max(last_change, last_change_json)

        # Get Min of TeX and SVG
        last_change_tex = min(last_change_tex, last_change_svg)

        return last_change > last_change_tex

    def make_svg(self):
        """
        Save the figure as SVG.
        """

        if not os.path.exists(os.path.dirname(self.filename_svg)):
            os.makedirs(os.path.dirname(self.filename_svg))

        self.savefig(self.filename_svg, format=self.format)

    def make_tex(self):
        """
        Save the figure as a tex file.
        """

        if not os.path.exists(os.path.dirname(self.filename_tex)):
            os.makedirs(os.path.dirname(self.filename_tex))

        include_function = 'includesvg' if self.format == 'svg' else 'includegraphics'

        with open(self.filename_tex, 'w') as f:
            f.write(f"""% TEX root = ../../../Main.tex
% Path: {self.filename_tex}
\\begin{{figure}}[H]
    \\centering
    \\{include_function}[width=0.95\\textwidth]{{{self.filename_svg}}} % Include the {self.format} file
    \\caption{{{self.caption}}}
    \\label{{fig:{self.basename}}}
\\end{{figure}}""")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is SkipWithBlock:
            return True
        elif exc_type is not None:
            print(f'\x1b[1;31m[ERROR]\x1b[0m {exc_val}')
            return False

        self.make_svg()
        self.make_tex()
        print(f'\x1b[1;32m[INFO]\x1b[0m Saved {self.basename}')