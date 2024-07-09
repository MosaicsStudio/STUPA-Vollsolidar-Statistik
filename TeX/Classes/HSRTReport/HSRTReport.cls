% !TEX root = ../../../Main.tex

% Suppress all warnings; Only show errors
\usepackage{silence}
\WarningsOff*

% If not using XeTeX, print an error message and stop compiling
\ifx\XeTeXversion\undefined
    \PackageError{HSRTReport}{This class can only be used with XeLaTeX.}{}
    \stop
\fi

%----------------------------------------
%   PATHS
%----------------------------------------
\def\fontsPath{TeX/Assets/Fonts}
\def\imagesPath{TeX/Assets/Images}
\def\classPath{TeX/Classes/HSRTReport}

%----------------------------------------
%   CLASS DEFINITION AND PARAMETERS
%----------------------------------------
% Original: ZHAWReport.cls by Martin Oswald
\NeedsTeXFormat{LaTeX2e}
\newcommand{\classname}{TeX/Classes/HSRTReport/HSRTReport}
\ProvidesClass{\classname}[2024/07/08 HSRT Report Class]
\providecommand{\baseclass}{scrreprt}

% Default options
\PassOptionsToClass{pointlessnumbers}{\baseclass}

% Forward options to the base class
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{\baseclass}}
\ProcessOptions\relax

% Load the base class with options
\LoadClass{\baseclass}

%----------------------------------------
%   REQUIRED PACKAGES
%----------------------------------------
\RequirePackage[ngerman,english]{babel}
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
\hypersetup{
    pdfpagemode={UseOutlines},
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


%----------------------------------------
%   PAGE SETUP
%----------------------------------------

\pagestyle{fancy}

\renewcommand{\headrulewidth}{0pt}

%----------------------------------------
%   LOGOS
%----------------------------------------

% ==== Add more logos to be placed besides the main logo on the title page ====
\newcommand{\titlePageLogosArray}{}
\newcommand{\footerLogosArray}{}
\newcommand{\logosScale}{1}
\newcommand{\mainLogoScale}{1}

\newlength{\imageHeight}

\newcounter{logoCounter}
\setcounter{logoCounter}{1}

\DeclareRobustCommand{\SetLogosScale}[1]{
    \renewcommand{\logosScale}{#1}
}

\DeclareRobustCommand{\AddLogo}[5]{
    \appto{\titlePageLogosArray}{
        \node[anchor=west, xshift=0.5cm] (logo#4) at (logo#5.east) {
            \setlength{\imageHeight}{1.5cm*\real{#2}*\real{\logosScale}}
            \StrBehind{#1}{.}[\fileExtension]
            \strcompare{\fileExtension}{svg}{
                \includesvg[height=\imageHeight]{#1}
            }{
                \includegraphics[height=\imageHeight]{#1}
            }
        };
        \filldraw[white, opacity=#3] (logo#4.north east) rectangle (logo#4.south west);
    }

    \appto{\footerLogosArray}{
        \node[anchor=east, xshift=-0.1cm] (logo#4) at (logo#5.west) {
            \setlength{\imageHeight}{1.5cm*\real{#2}*\real{0.55}*\real{\logosScale}}
            \StrBehind{#1}{.}[\fileExtension]
            \strcompare{\fileExtension}{svg}{
                \includesvg[height=\imageHeight]{#1}
            }{
                \includegraphics[height=\imageHeight]{#1}
            }
        };
        \filldraw[white, opacity=#3] (logo#4.north east) rectangle (logo#4.south west);
    }
}

\DeclareRobustCommand{\SetupTitlePageLogos}{
    \titlePageLogosArray
}

\DeclareRobustCommand{\SetupFooterLogos}{
    \footerLogosArray
}
% =============================================================================
\def\skylinePath{TeX/Assets/Images/Skyline.svg}

\newcommand{\footerYShift}{0.7em}
\newcommand{\footerXShift}{0.7em}

% Define the logo and its position
\AtBeginPage{
    \setlength{\imageHeight}{2cm*\real{\mainLogoScale}*\real{\logosScale}*\real{0.45}}
    \begin{tikzpicture}[overlay, remember picture]
        \node[anchor=south east, inner sep=0pt, xshift=-\footerXShift, yshift=\footerYShift] (logo0) at (current page.south east) {
            \strcompare{\thepage}{1}{}{
                \includesvg[height=\imageHeight]{\imagesPath/DUMMY_FOOT.svg}
            }
        };
        \SetupFooterLogos
        \node[anchor=south west, inner sep=0pt, yshift=0em] at (current page.south west) {
            \includesvg[width=1.5\paperwidth]{\skylinePath}
        };
        \filldraw[white] (logo0.north east) rectangle (logo0.south west);
    \end{tikzpicture}
}

%----------------------------------------
%   TITLE PAGE
%----------------------------------------
\setkomafont{pagenumber}{\color{gray}\blenderfont\selectfont}

\fancyhf{}
\fancyhead[L]{\color{gray}\blenderfont \@title}
\fancyhead[R]{\pagemark}
\fancyfoot[C]{}

\fancypagestyle{fancy}{
    \fancyhf{}
    \fancyhead[L]{\color{gray}\blenderfont \@title}
    \fancyhead[R]{\pagemark}
    \fancyfoot[C]{}
}

% Set font for all headings
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

\input{\classPath/Pages/Titlepage.tex}

%----------------------------------------
%   TABLE OF CONTENTS
%----------------------------------------
%\usepackage{tocloft}
%\renewcommand{\cftpartleader}{\cftdotfill{\cftdotsep}} % for parts
%\renewcommand{\cftchapleader}{\cftdotfill{\cftdotsep}} % for chapters

% Set Chapter font size in TOC
%\renewcommand{\cftchapfont}{\sffamily\bfseries\large}
