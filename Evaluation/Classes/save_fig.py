#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Save figures to the Output/Images folder.
"""

import os
from matplotlib.figure import Figure

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
        return self
    
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
            f.write(f"""
\\begin{{figure}}[H]
    \\centering
    \\{include_function}{{\\path{{{self.filename_svg}}}}} % Include the {self.format} file
    \\caption{{{self.caption}}}
    \\label{{fig:{self.basename}}}
\\end{{figure}}""")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.make_svg()
        self.make_tex()
        print(f'\x1b[1;32m[INFO]\x1b[0m Saved {self.basename}')