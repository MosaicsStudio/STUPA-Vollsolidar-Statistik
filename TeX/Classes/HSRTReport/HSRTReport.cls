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

\newcommand{\footerYShift}{0.4em}
\newcommand{\footerXShift}{0.7em}

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
\newcommand{\shadesArray}{}
\newcommand{\logosScale}{1}
\newcommand{\mainLogoScale}{1}

\newcommand{\lastToken}{mainLogo}

\DeclareRobustCommand{\SetLogosScale}[1]{
    \renewcommand{\logosScale}{#1}
}

\DeclareRobustCommand{\AddLogo}[3]{
    \edef\currentTokenEval{\lastToken Next}
    \edef\lastTokenEval{\lastToken}

    \appto{\titlePageLogosArray}{
        \node[anchor=west, xshift=0.5cm] (\currentTokenEval) at (\lastTokenEval.east) {
            \includegraphics[height=2cm*\real{#2}*\real{\logosScale}]{#1}
        };
    }

    \appto{\footerLogosArray}{
        \node[anchor=east, xshift=-0.1cm] (\currentTokenEval) at (\lastTokenEval.west) {
            \strcompare{\thepage}{1}{}{
                \includegraphics[height=2cm*\real{#2}*\real{0.65}*\real{\logosScale}]{#1}
            }
        };
    }

    \ifx#3\empty
        \edef\shadeOpacity{0}
    \else
        \edef\shadeOpacity{#3}
    \fi

    \appto{\shadesArray}{
        \filldraw[white, opacity=\shadeOpacity] (\currentTokenEval.north east) rectangle (\currentTokenEval.south west);
    }

    \renewcommand{\lastToken}{\currentTokenEval}
}

\DeclareRobustCommand{\AddMask}[2]{
    \appto{\shadesArray}{
        \filldraw[white, opacity=#2] (#1.north east) rectangle (#1.south west);
    }
}

\DeclareRobustCommand{\ShadeMainLogo}[1]{
    \AddMask{mainLogo}{#1}
}

\DeclareRobustCommand{\SetupTitlePageLogos}{
    \titlePageLogosArray\shadesArray
}

\DeclareRobustCommand{\SetupFooterLogos}{
    \footerLogosArray\shadesArray
}
% =============================================================================

\def\stupa{STUPA}

\providecommand{\mainLogo}{\strcompare{\logoType}{\stupa}{STUPA.png}{HSRT.png}}

\DeclareRobustCommand{\SetMainLogo}[2]{
    \renewcommand{\mainLogo}{#1}

    \ifx#2\empty
        \renewcommand{\mainLogoScale}{1}
    \else
        \renewcommand{\mainLogoScale}{#2}
    \fi
}

% If \logoType is equal to STUPA, set logo to STUPA logo else set it to HSRT logo
\newcommand{\logoPath}{
    \imagesPath/\mainLogo
}

\def\skylinePath{TeX/Assets/Images/Skyline.svg}

% Define the logo and its position
\AtBeginPage{
    \begin{tikzpicture}[overlay, remember picture]
        \node[anchor=south east, inner sep=0pt, xshift=-\footerXShift, yshift=\footerYShift] (mainLogo) at (current page.south east) {
            \strcompare{\thepage}{1}{}{
                \includegraphics[height=2cm*\real{\mainLogoScale}*\real{0.65}*\real{\logosScale}]{\logoPath}
            }
        };
        \SetupFooterLogos
        \node[anchor=south west, inner sep=0pt, yshift=0em] at (current page.south west) {
            \includesvg[width=1.5\paperwidth]{\skylinePath}
        };
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
