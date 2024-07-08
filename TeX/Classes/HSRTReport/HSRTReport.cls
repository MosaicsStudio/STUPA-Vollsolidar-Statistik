% !TEX root = ../../../Main.tex

%----------------------------------------
%   CLASS DEFINITION AND PARAMETERS
%----------------------------------------
\NeedsTeXFormat{LaTeX2e}
\newcommand{\classname}{zhawreport}
\ProvidesClass{\classname}[2023/11/13 ZHAW Report]
\providecommand{\baseclass}{scrreprt}

% default options
\PassOptionsToClass{pointlessnumbers}{\baseclass}

% forward options to the base class
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{\baseclass}}
\ProcessOptions\relax

% load the base class with options
\LoadClass{\baseclass}

%----------------------------------------
%   REQUIRED PACKAGES
%----------------------------------------
\RequirePackage[english]{babel}
\RequirePackage{parskip}
\RequirePackage{lmodern}
\RequirePackage{amsmath}
\RequirePackage{graphicx}
\RequirePackage{svg}
\RequirePackage[T1]{fontenc}
\RequirePackage{fontspec}
\RequirePackage{tikz}
\RequirePackage{fancyhdr}
\RequirePackage{bophook}
\RequirePackage{ifthen}

%----------------------------------------
%   REFS
%----------------------------------------
\RequirePackage{hyperref}
\hypersetup{pdfpagemode={UseOutlines},
    bookmarksopen=true,
    bookmarksopenlevel=0,
    hypertexnames=false,
    colorlinks=true,
    citecolor=[rgb]{0.286, 0.427, 0.537},
    linkcolor=[rgb]{0.161, 0.31, 0.427},
    urlcolor=[rgb]{0.071, 0.212, 0.322},
    pdfstartview={FitV},
    unicode,
    breaklinks=true
}

%----------------------------------------
%   FONT SETUP
%----------------------------------------
\renewcommand*\rmdefault{lmr}
\renewcommand*\sfdefault{lmss}

\newcommand{\footerYShift}{0.4em} % Added the new variable
\newcommand{\footerXShift}{0.7em} % Added the new variable

\def\fontsPath{TeX/Assets/Fonts}

\newfontfamily\blenderfont[
    Path=\fontsPath/Blender/,
    Extension=.ttf,
    UprightFont=*-Medium,
    BoldFont=*-Bold,
    ItalicFont=*-MediumItalic,
    BoldItalicFont=*-BoldItalic
]{Blender}
\newfontfamily\dinfont[
    Path=\fontsPath/DIN/,
    Extension=.ttf,
    UprightFont=*-Regular,
    BoldFont=*-Bold,
    ItalicFont=*-Italic,
    BoldItalicFont=*-BoldItalic
]{DIN}

\setsansfont{Blender}[
    Path=\fontsPath/Blender/,
    Extension=.ttf,
    UprightFont=*-Medium,
    BoldFont=*-Bold,
    ItalicFont=*-MediumItalic,
    BoldItalicFont=*-BoldItalic
]
\setmainfont{DIN}[
    Path=\fontsPath/DIN/,
    Extension=.ttf,
    UprightFont=*-Regular,
    BoldFont=*-Bold,
    ItalicFont=*-Italic,
    BoldItalicFont=*-BoldItalic
]

\pagestyle{fancy}

\renewcommand{\headrulewidth}{0pt}

% Define the logo and its position
\AtBeginPage{
    \begin{tikzpicture}[overlay, remember picture]
        \node[anchor=south east, inner sep=0pt, xshift=-\footerXShift, yshift=\footerYShift] at (current page.south east) {
            \ifthenelse{\thepage>1}{
                \includegraphics[width=3.25cm]{TeX/Assets/Images/Stupa.png}
            }{}
        };
        \node[anchor=south west, inner sep=0pt, yshift=0em] at (current page.south west) {
            \includesvg[width=1.5\paperwidth]{TeX/Assets/Images/Skyline.svg}
        };
    \end{tikzpicture}
}

\setkomafont{pagenumber}{\color{gray}\blenderfont\selectfont}

\fancyhf{}
\fancyhead[L]{\color{gray}\blenderfont Survey on the Support of the Deutschlandticket in the Full-Solidarity-Model}
\fancyhead[R]{\pagemark}

\setkomafont{disposition}{\sffamily\bfseries}
\setkomafont{chapter}{\Large\sffamily\bfseries}
\setkomafont{section}{\Large\sffamily\bfseries}
\setkomafont{subsection}{\large\sffamily\bfseries}
\setkomafont{subsubsection}{\large\sffamily\bfseries}

\RedeclareSectionCommand[
    beforeskip=1ex,
    afterskip=0.5ex,
    style=section
]{chapter}

\RedeclareSectionCommands[
    beforeskip=0.6ex,
    afterskip=0.3ex,
]{section,subsection,subsubsection}

\newcommand{\decoRule}{\rule{.8\textwidth}{.4pt}}

\input{TeX/Classes/HSRTReport/Pages/Titlepage.tex}