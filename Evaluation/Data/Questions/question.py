#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes for the evaluation of the questionnaire
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd
from pandas import DataFrame
from matplotlib.figure import Figure

import numpy as np

import matplotlib.pyplot as plt

class Option:
    __text: str = ''
    __code: str = ''

    def __init__(self, code: str, text: str):
        self.__code = code
        self.__text = text

    def __str__(self) -> str:
        return self.__key
    
    def __repr__(self) -> str:
        return f'Option("{self.__code}", "{self.__text}")'
    
    @property
    def text(self) -> str:
        return self.__text
    
    @property
    def code(self) -> str:
        return self.__code

class QuestionType(Enum):
    OPTIONS = 'options'
    RANKING = 'ranking'
    TEXT = 'text'
    NUMBER = 'number'

class Correlation:
    question_a: 'Question'
    question_b: 'Question'

    def __init__(self, question_a: 'Question', question_b: 'Question'):
        self.question_a = question_a
        self.question_b = question_b

    def __str__(self) -> str:
        return f'{self.question_a.text}\nvs. {self.question_b.text}'
    
    def __repr__(self) -> str:
        return f'Correlation({self.question_a}, {self.question_b})'
    
    def scatter_plot(self, df: DataFrame, fig: Figure, **kwargs: Any) -> None:
        if self.question_a.type != QuestionType.NUMBER or self.question_b.type != QuestionType.NUMBER:
            raise ValueError("Both questions must be of type 'number' for a scatter plot")

        df.plot.scatter(x=self.question_a.code, y=self.question_b.code, title=str(self), ax=fig.gca(), **kwargs)

    def scatter_with_category(
            self,
            df: DataFrame,
            fig: Figure,
            category: 'Question',
            x_log: bool=False,
            y_log: bool=False,
            colors: List[str]=[],
            show_regression: bool=False,
            **kwargs: Any
        ) -> None:
        if self.question_a.type != QuestionType.NUMBER or self.question_b.type != QuestionType.NUMBER:
            raise ValueError("Both questions must be of type 'number' for a scatter plot")

        ax = fig.gca()

        if category.type != QuestionType.OPTIONS:
            match category.type:
                case QuestionType.RANKING:
                    df, category = category.merge_ranks(df)
                case _:
                    raise ValueError(f"Category type '{category.type}' not supported for scatter plot")
    
        # Convert Question columns to numeric
        self.question_a.make_numeric(df)
        self.question_b.make_numeric(df)

        for i, (key, group) in enumerate(category.group_frame(df)):
            ax = group.plot.scatter(
                x=self.question_a.code,
                y=self.question_b.code,
                title=f'{str(self)} for {category.text_of_option(key)}',
                ax=ax,
                color=colors[i] if i < len(colors) else None,
                label=category.text_of_option(key),
                **kwargs
            )

            if show_regression:
                x = group[self.question_a.code]
                y = group[self.question_b.code]

                m, b = np.polyfit(x, y, 1)

                ax.plot(x, m*x + b, color='black')

        if x_log:
            ax.set_xscale('log')
        if y_log:
            ax.set_yscale('log')

        # Add Axis Labels
        ax.set_xlabel(self.question_a.text)
        ax.set_ylabel(self.question_b.text)

        ax.legend(title=category.text, loc='upper left')

class Page:
    __questions: List['Question']
    __code: str = ''
    __text: str = ''

    # Static property for all pages
    PAGES: Dict[str, 'Page'] = {}
    
    @staticmethod
    def add_page(page: 'Page') -> None:
        Page.PAGES[page.code] = page

    def __init__(self, code: str, text: str, questions: List['Question'] | 'Question'):
        global PAGES

        self.__questions = questions if isinstance(questions, list) else [questions]
        self.__code = code
        self.__text = text

        Page.add_page(self)

    def __getitem__(self, key: str) -> 'Question':
        for question in self.__questions:
            if question.code == key:
                return question

        raise KeyError(f"Question '{key}' not found in page '{self.__text}'")
    
    @property
    def text(self) -> str:
        return self.__text
    
    @property
    def code(self) -> str:
        return self.__code
    
    @property
    def questions(self) -> List['Question']:
        return self.__questions
    
    @property
    def time(self) -> 'Question':
        group_number = int(self.code.split('G')[1])
        code = f'groupTime{group_number}'

        return Question(
            code,
            f'{self.text} Time',
            {},
            QuestionType.NUMBER
        )
    
    def add_question(self, question: 'Question' | List['Question']) -> None:
        if isinstance(question, list):
            self.__questions.extend(question)
        else:
            self.__questions.append(question)

# Labels for the groups
class Question:
    __answers: Dict[str, Option] = {}
    __text: str = ''
    __code: str = ''
    __type: str = ''
    __ranking_slots: int = 0

    __page: Page = None

    def __init__(self, code: str, text: str, answers: Dict[str, str], type: str = QuestionType.OPTIONS, ranking_slots: int = 0):
        self.__answers = {key: Option(key, text) for key, text in answers.items()}
        self.__text = text
        self.__code = code

        assert type in QuestionType.__members__.values(), f"Type '{type}' not found in QuestionType"
        self.__type = type

        assert type != QuestionType.RANKING or ranking_slots > 0, "Ranking questions need a number of slots"
        self.__ranking_slots = ranking_slots

        # Add the question to the respective page
        page_code = self.page_code

        if page_code in Page.PAGES:
            Page.PAGES[page_code].add_question(self)
        else:
            Page(page_code, f'Page {page_code}', self)

        self.__page = Page.PAGES[page_code]

    def __getitem__(self, key: str) -> str:
        # If Key is like 'AO{XX}' or an integer, return the text of the option
        if key in self.__answers:
            return self.__answers[key]
        elif isinstance(key, int) and (key := f'AO{int(key):02}') in self.__answers:
            return self.__answers[key]
        else:
            raise KeyError(f"Key '{key}' not found in question '{self.__text}'")
        
    def __str__(self) -> str:
        return self.__text
    
    def __repr__(self) -> str:
        return f'Question("{self.__code}", "{self.__text}", {self.__answers})'
    
    @property
    def text(self) -> str:
        return self.__text

    @property
    def code(self) -> str:
        return self.__code
    
    @property
    def answers(self) -> Dict[str, Option]:
        return self.__answers
    
    @property
    def type(self) -> str:
        return self.__type
    
    @property
    def ranking_slots(self) -> List[str]:
        return [
            self.ranking_nth(i) for i in range(1, self.__ranking_slots + 1)
        ]
    
    @property
    def page_code(self) -> str:
        return self.__code.split('Q')[0]
    
    @property
    def page(self) -> Page:
        return self.__page if self.__page is not None else Page.pages[self.page_code]
    
    @property
    def time(self) -> 'Question':
        return self.page.time

    def text_of_option(self, key: str) -> str:
        if key is None or key == '':
            return None

        try:
            return self[key].text
        except KeyError:
            return key

    def group_frame(self, df: DataFrame) -> DataFrame:
        return df.groupby(self.code)
    
    def rename_index(self, df: DataFrame) -> None:
        return df.rename(index=self.__answers, inplace=True)
    
    def rename_columns(self, df: DataFrame) -> None:
        return df.rename(columns=self.__answers, inplace=True)
    
    def ranking_nth(self, nth: int) -> str:
        assert self.__type == QuestionType.RANKING, "Question is not a ranking question"
        assert 0 < nth <= self.__ranking_slots, f"Ranking slot {nth} is out of range"
        return f'{self.code}[{nth}]'
    
    def ranking_nth_question(self, nth: int) -> str:
        return Question(
            self.ranking_nth(nth),
            f'{self.text} (Ranking Slot {nth})',
            {key: option.text for key, option in self.__answers.items()},
            QuestionType.OPTIONS
        )
    
    def answered(self, df: DataFrame) -> DataFrame:
        return df[df[self.code].notnull()]
    
    def of_answer(self, df: DataFrame, answer: str | int | List[str | int]) -> DataFrame:
        if isinstance(answer, int):
            answer = f'AO{answer:02}'

        if isinstance(answer, list):
            return df[df[self.code].isin(answer)]

        assert answer in self.__answers, f"Answer '{answer}' not found in question '{self.__text}'"

        return df[df[self.code] == answer]
    
    def merge_ranks(self, df: DataFrame) -> Tuple[DataFrame, 'Question']:
        assert self.__type == QuestionType.RANKING, "Question is not a ranking question"

        # Options
        options = list(self.__answers.keys())

        column_name = f'{self.code}_MERGED'

        all_columns_list = list(df.columns)

        # Create a new DataFrame for the ranking; Have one column per option with the numeric sum for the respective row and option
        new_df = DataFrame(columns=[column_name, *all_columns_list])

        for rank in range(1, self.__ranking_slots + 1):
            weight_factor = (self.__ranking_slots + 1 - rank)

            # Get the column for the current rank
            column = self.ranking_nth(rank)

            for row in df.iterrows():
                for option in options:
                    if row[1][column] == option:
                        # Add the answer `weight_factor` times to the new DataFrame
                        for _ in range(weight_factor):
                            new_df.loc[len(new_df)] = [option, *row[1]]

        return new_df, Question(column_name, f'{self.text} (Merged)', {key: option.text for key, option in self.__answers.items()}, QuestionType.OPTIONS)
    
    def against(self, other: 'Question') -> Correlation:
        return Correlation(self, other)

    def pie_plot(self, df: DataFrame, fig: Figure, colors_mapped: str=dict(), **kwargs: Any) -> None:
        if self.type != QuestionType.OPTIONS:
            match self.type:
                case QuestionType.RANKING:
                    df_merged, question_merged = self.merge_ranks(df)

                    question_merged.pie_plot(df_merged, fig, colors_mapped=colors_mapped, **kwargs)
                case _:
                    raise ValueError(f"Question type '{self.type}' not supported for pie plot")
        else:
            counts = df.groupby(self.code).size()
            counts.index = [self.text_of_option(index) for index in counts.index]
            ax = counts.plot(kind='pie', autopct='%1.1f%%', title=self.text, ax=fig.gca(), **kwargs)
            ax.axis('equal')

            labels_groups = [node for node in ax.texts if '%' not in node.get_text()]

            for label in labels_groups:
                label_text = label.get_text()

                if '%' in label_text:
                    foreground = 'white'
                    background = 'black'
                else:
                    foreground = 'black'
                    background = 'white'

                    if label_text in colors_mapped:
                        foreground = colors_mapped[label_text]

                label.set_fontsize(12)
                label.set_fontweight('bold')
                label.set_bbox(dict(facecolor=background, alpha=0.5, edgecolor=foreground, boxstyle='round,pad=0.2'))
                label.set_color(foreground)

    def make_numeric(self, df: DataFrame) -> None:
        df[self.code] = pd.to_numeric(df[self.code], errors='coerce')

    def filter_numeric(self, df: DataFrame, filter: Callable[..., bool]) -> DataFrame:
        self.make_numeric(df)
        return df[filter(df[self.code])]