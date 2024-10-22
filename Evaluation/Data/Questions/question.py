#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes for the evaluation of the questionnaire
"""

from enum import Enum
import glob
import math
import os
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd
from pandas import DataFrame
from matplotlib.figure import Figure

import numpy as np

import matplotlib.pyplot as plt

import pickle

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
        return f'{self.question_a.text}\nagainst {self.question_b.text}'
    
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

        labels: List[str] = []
        ax_plot_params: List[Tuple[List[Any], Dict[str, Any]]] = []

        for i, (key, group) in enumerate(category.group_frame(df)):
            ax = group.plot.scatter(
                x=self.question_a.code,
                y=self.question_b.code,
                title=f'{str(self)}\nby {category.text}',
                ax=ax,
                color=colors[i] if i < len(colors) else None,
                label=category.text_of_option(key),
                **kwargs
            )

            if show_regression:
                x = group[self.question_a.code]
                y = group[self.question_b.code]

                # zip and sort by x
                x, y = zip(*sorted(zip(x, y), key=lambda t: t[0]))

                m, b = np.polyfit(x, y, 1)

                # Modify legend entry to have an m=... and b=... entry
                labels.append(f'{category.text_of_option(key)} (m={m:.2f}, b={b:.2f})')

                # Add the plot parameters for the regression line
                ax_plot_params.append((
                    [x, m * np.array(x) + b],
                    {
                        'color': colors[i] if i < len(colors) else None
                    }
                ))

        ax.legend(labels, title=category.text, loc='upper left')

        for plot_params in ax_plot_params:
            ax.plot(*plot_params[0], **plot_params[1])

        if x_log:
            ax.set_xscale('log')
        if y_log:
            ax.set_yscale('log')

        # Add Axis Labels
        ax.set_xlabel(self.question_a.text)
        ax.set_ylabel(self.question_b.text)

    def bar_options_plot(self, fig: Figure, df: pd.DataFrame, title: str, normalize=False, graph_mode='bars', color_palette=[], counts_text_color='black', color_palette_mapped=[], custom_y_text=None, custom_x_text=None):
        if self.question_a.type != QuestionType.OPTIONS:
            raise ValueError(f"Question type '{self.question_a.type}' not supported for bar plot")
            
        FACTOR = 1
        
        if self.question_b.type != QuestionType.OPTIONS:
            if self.question_b.type == QuestionType.RANKING:
                FACTOR = sum(range(1, len(self.question_b.ranking_slots)+1))
                df, self.question_b = self.question_b.merge_ranks(df)
            else:
                raise ValueError(f"Question type '{self.question_b.type}' not supported for bar plot")
        
        # Create a new DataFrame with the counts of the values
        counts = df.groupby([self.question_a.code, self.question_b.code]).size().unstack().fillna(0)

        # Rename the feature columns
        counts.columns = [self.question_b.text_of_option(col) for col in counts.columns]

        # Remove all columns that are None
        try:
            counts = counts.drop(columns=[None])
        except KeyError:
            pass

        # Rename the group columns
        counts.index = [self.question_a.text_of_option(col) for col in counts.index]

        # Normalize the values
        if normalize:
            counts_norm = counts.div(counts.sum(axis=1), axis=0)
        else:
            # Divide by the factor
            counts_norm = counts / FACTOR

        # Plot the values
        if graph_mode == 'bars':
            ax = counts_norm.plot(kind='bar', stacked=True, figsize=(10, 6), title=title, ax=fig.gca(), color=color_palette)
        else:
            raise ValueError(f"Invalid type: {graph_mode}")
        ax.set_xlabel(self.question_a.text if custom_x_text is None else custom_x_text)
        ax.set_ylabel('Shares per group' if normalize else 'Count' if custom_y_text is None else custom_y_text)

        # Get text size based on length
        max_len = max([len(str(col)) for col in counts_norm.index])
        text_size = 20 * (1 / (max_len / 10 + 1))

        # Adjust x-Axis text-size and orientation to fit the image
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha='center', va='top', fontsize=text_size)

        # Add Counts text of whole group to the top of the bars
        if normalize and FACTOR == 1:
            for group in counts_norm.index:
                total_height = ax.get_ylim()[1]
                bars_stacked_height = counts_norm.loc[group].sum()

                center = (total_height - bars_stacked_height) / 2 + bars_stacked_height

                label = ax.text(
                    # At the position of the group
                    x=counts_norm.index.get_loc(group),
                    # At the top of the bar
                    y=center if normalize else (counts_norm.loc[group].max()),
                    s=f"{counts.loc[group].sum()/FACTOR:.0f}",
                    ha='center', va='center' if normalize else 'bottom', color=counts_text_color
                )

                foreground = color_palette_mapped[group] if group in color_palette_mapped else 'black'

                label.set_fontsize(10)
                label.set_fontweight('bold')
                label.set_color(foreground)

        # Add the legend
        ax.legend(title=self.question_b.text)

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

    __cached_merged: List[Tuple[DataFrame, DataFrame, 'Question']] = []
    __cached_num2bin: List[Tuple[DataFrame, DataFrame, 'Question']] = []

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
        elif isinstance(key, int):
            if (key_str := f'AO{int(key):02}') in self.__answers:
                return self.__answers[key_str]
            else:
                return list(self.__answers.values())[key]
        elif isinstance(key, str) and key.startswith('AO') and key[2:].isnumeric():
            if key in self.__answers:
                return self.__answers[key]
            else:
                if int(key[2:]) >= len(self.__answers):
                    raise KeyError(f"Key '{key}' not found in question '{self.__text}'")
                return list(self.__answers.values())[int(key[2:])]
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
        return df[df[self.code].notnull() & (df[self.code] != '')]
    
    def of_answer(self, df: DataFrame, answer: str | int | List[str | int]) -> DataFrame:
        if isinstance(answer, int):
            answer = f'AO{answer:02}'

        if isinstance(answer, list):
            return df[df[self.code].isin(answer)]

        assert answer in self.__answers, f"Answer '{answer}' not found in question '{self.__text}'"

        return df[df[self.code] == answer]
    
    def save_cache(self, path: str='Evaluation/cache.pkl') -> None:
        # Pickle the cache
        with open(path, 'wb') as f:
            pickle.dump(self.__cached_merged, f)

    def load_cache(self, path: str='Evaluation/cache.pkl') -> None:
        # Load the cache
        with open(path, 'rb') as f:
            self.__cached_merged = pickle.load(f)

    def is_saved_cache_recent(self, path: str='Evaluation/cache.pkl') -> bool:
        if not os.path.exists(path):
            return False

        # Get the timestamp the newest .json file was created/modified
        cache_time = os.path.getmtime(path)
        source_time = os.path.getmtime(max(glob.iglob('Evaluation/Data/*.json'), key=os.path.getmtime))

        return cache_time >= source_time

    def get_cached_merged(self, df: DataFrame) -> Tuple[DataFrame, 'Question']:
        if self.__cached_merged is None or len(self.__cached_merged) == 0:
            if self.is_saved_cache_recent():
                self.load_cache()

        for cached in self.__cached_merged:
            if cached[0].equals(df):
                return cached[1], cached[2]

        return None, None
    
    def add_cached_merged(self, df: DataFrame, merged: DataFrame, question: 'Question') -> None:
        self.__cached_merged.append((df, merged, question))

        self.save_cache()

    def get_cached_num2bin(self, df: DataFrame) -> Tuple[DataFrame, 'Question']:
        if self.__cached_num2bin is None or len(self.__cached_num2bin) == 0:
            if self.is_saved_cache_recent():
                self.load_cache('Evaluation/cache_num2bin.pkl')

        for cached in self.__cached_num2bin:
            if cached[0].equals(df):
                return cached[1], cached[2]

        return None, None
    
    def add_cached_num2bin(self, df: DataFrame, merged: DataFrame, question: 'Question') -> None:
        self.__cached_num2bin.append((df, merged, question))

        self.save_cache('Evaluation/cache_num2bin.pkl')

    def merge_ranks(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, 'Question']:
        assert self.__type == QuestionType.RANKING, "Question is not a ranking question"

        df_cached, question_cached = self.get_cached_merged(df)

        if df_cached is not None:
            return df_cached, question_cached

        # Options
        options = list(self.__answers.keys())

        column_name = f'{self.code}_MERGED'

        # Calculate multipliers for each rank
        factor = math.lcm(*[math.prod([x for x in range(1, self.__ranking_slots + 1) if x != i]) for i in range(1, self.__ranking_slots + 1)])
        multipliers = [int(factor / x) for x in range(1, self.__ranking_slots + 1)]

        print(f'Multipliers: {multipliers}')

        # Create a DataFrame to store weighted rows
        expanded_rows = []

        for rank, weight_factor in zip(range(1, self.__ranking_slots + 1), multipliers):
            column = self.ranking_nth(rank)
            for option in options:
                # Filter rows where the option is selected for the current rank
                matched_rows = df[df[column] == option]
                # Append each row 'weight_factor' times
                for row in matched_rows.itertuples(index=False, name=None):
                    expanded_rows.extend([option] + list(row) for _ in range(weight_factor))

        # Create a new DataFrame from the expanded rows
        new_df = pd.DataFrame(expanded_rows, columns=[column_name, *df.columns])

        question_merged = Question(column_name, f'{self.text} (Merged)', {key: option.text for key, option in self.__answers.items()}, QuestionType.OPTIONS)

        self.add_cached_merged(df, new_df, question_merged)

        return new_df, question_merged
    
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

            previous_label = None

            for label in ax.texts:
                label_text: str = label.get_text()

                foreground = 'black'
                background = 'white'

                if label_text in colors_mapped:
                    foreground = colors_mapped[label_text]

                label.set_fontsize(10)
                label.set_fontweight('bold')
                label.set_bbox(dict(facecolor=background, alpha=0.5, edgecolor=foreground, boxstyle='round,pad=0.2'))
                label.set_color(foreground)

                previous_label = label_text

    def make_numeric(self, df: DataFrame) -> None:
        df[self.code] = pd.to_numeric(df[self.code], errors='coerce')

    def filter_numeric(self, df: DataFrame, filter: Callable[..., bool]) -> DataFrame:
        self.make_numeric(df)
        return df[filter(df[self.code])]
    
    def histogram(self, df: DataFrame, fig: Figure, bins: int=10, **kwargs: Any) -> None:
        if self.type != QuestionType.NUMBER:
            raise ValueError(f"Question type '{self.type}' not supported for histogram")

        self.make_numeric(df)

        ax = fig.gca()

        # Add mean and median lines
        mean = df[self.code].mean()
        median = df[self.code].median()

        ax.axvline(mean, color='r', linestyle='dashed', linewidth=1)
        ax.axvline(median, color='g', linestyle='dashed', linewidth=1)

        ax.legend([f'Mean: {mean:.2f}', f'Median: {median:.2f}'])

        df[self.code].plot.hist(bins=bins, title=self.text, ax=ax, **kwargs)

    def numeric_to_bins_options(self, df: DataFrame, bin_size, min: float=None, max: float=None) -> Tuple[DataFrame, 'Question']:
        if self.type != QuestionType.NUMBER:
            raise ValueError(f"Question type '{self.type}' not supported for binning")
        
        if self.is_saved_cache_recent('Evaluation/cache_num2bin.pkl'):
            cached_df, question_binned = self.get_cached_num2bin(df)

            if cached_df is not None:
                return cached_df, question_binned

        self.make_numeric(df)

        column_name = f'{self.code}_BINS'

        # Get the min and max values
        min_value = df[self.code].min() if min is None else min

        # Get the max value
        max_value = (df[self.code].max() if max is None else max) + bin_size

        # Create the bins
        bins = np.arange(min_value, max_value, bin_size)

        # Create the labels
        labels = [f'{int(bins[i])}-{int(bins[i+1])}' for i in range(len(bins) - 1)]

        df_binned = df.copy()

        # Create the new column
        df_binned[column_name] = pd.cut(df[self.code], bins, labels=labels, include_lowest=True)

        question_binned = Question(column_name, f'{self.text} (Binned)', {label: f'{label}km' for i, label in enumerate(labels)}, QuestionType.OPTIONS)

        self.add_cached_num2bin(df, df_binned, question_binned)

        return df_binned, question_binned
