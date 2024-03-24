"""
Preprocessing functions for text data. 
Includes functions to clean text, remove stopwords, and combine columns.
"""

import re  # regex
from typing import List  # type hinting

import pandas as pd  # pandas for dataframes

from negexPython.negex import negTagger, sortRules


def clean_dataframe(df_data: pd.DataFrame,
                    text_columns: str,
                    drop_duplicates: bool = False,
                    drop_nulls: bool = False,
                    drop_negatives: bool = False,
                    drop_ambiguous: bool = False,
                    replace_connectors: bool = False) -> pd.DataFrame:
    """
    Clean dataframe by removing punctuation, new line characters, and trailing whitespace. 
    Make all text lowercase.
    Optionally drop duplicates, nulls, and empty rows.

    Args:
        df (pd.DataFrame): The dataframe to clean.
        text_columns (str): The column(s) to clean.
        drop_duplicates (bool, optional): Drop duplicate rows. Defaults to True.
        drop_nulls (bool, optional): Drop rows with null values. Defaults to True.

    Returns:
        pd.DataFrame: The cleaned dataframe.
    """
    for col in text_columns:

        if drop_duplicates:
            df_data = df_data.drop_duplicates(subset=[col])  # drop duplicates
        if drop_nulls:
            df_data = df_data.dropna(subset=[col])  # drop nulls


        df_data[col] = df_data[col].str.replace('\n', ' ', regex=True) # remove new line characters
        df_data[col] = df_data[col].str.replace('/', ' ', regex=True)  # remove forward slash
        df_data[col] = df_data[col].str.replace('-', ' ', regex=True)  # remove dash
        df_data[col] = df_data[col].str.replace('[^\w\s.]', '', regex=True)  # remove punctuation
        df_data[col] = df_data[col].str.replace('\s+', ' ', regex=True) # remove trailing whitespace
        df_data[col] = df_data[col].str.replace('\.$', '', regex=True)  # remove trailing period
        df_data[col] = df_data[col].str.lower()  # Convert to lowercase

        if drop_negatives:
            df_data[col] = df_data[col].apply(lambda x: remove_negated_phrases(x, rules=None,
                                                            drop_ambiguous=drop_ambiguous,
                                                            replace_connectors=replace_connectors))
        return df_data


def remove_stopwords(df: pd.DataFrame,
                     text_columns: List[str],
                     stop_words: List[str] = None
                     ) -> pd.DataFrame:
    """
    Remove stopwords from text columns.

    Args:
        df (pd.DataFrame): Dataframe to remove stopwords from.
        text_columns (list[str]): The text columns to remove stopwords from.
        stop_words (list[str], optional): List of stopwords. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe with stopwords removed.
    """

    if stop_words is None:  # if no stopwords are provided, use nltk stopwords with some exceptions

        # Load stopwords from csv]
        stop_words = pd.read_csv('data/stopwords.csv').T.values[0]
        exceptions = ['no', 'not', 'nor', 'few', 'other']
        stop_words = [re.sub('[^\w\s]', '', s)
                      for s in stop_words]  # remove punctuation
        stop_words = [word for word in stop_words if word not in exceptions]

    stop_words = set(stop_words)

    for col in text_columns:  # Remove stopwords from text in each column using regex
        df[col] = df[col].apply(lambda x: re.sub(
            r'\b(' + r'|'.join(stop_words) + r')\b\s*', '', x))

    return df


def combine_colums(df: pd.DataFrame,
                   cols: list,
                   new_col_name: str = 'combined',
                   delimiter: str = ' ',
                   inplace=False
                   ) -> pd.DataFrame:
    """
    Combine multiple columns with strings into a single column.

    Args:
        df (pd.DataFrame): The dataframe to combine columns in.
        cols (list): The columns to combine.
        new_col_name (str, optional): The name of the new column. Defaults to 'combined'.
        delimiter (str, optional): The delimiter to use between columns. Defaults to ' '.
        inplace (bool, optional): Whether to modify the dataframe inplace. Defaults to False.

    Returns:
        pd.DataFrame: The dataframe with the columns combined.
    """

    df_copy = df.copy()  # make a copy of the dataframe

    df_copy[new_col_name] = df_copy[cols[0]]
    for col in cols[1:]:
        df_copy[new_col_name] += delimiter + df_copy[col]

    if inplace:
        df_copy.drop(columns=cols, inplace=True)

    return df_copy


def remove_negated_phrases(text:str,
                           rules:List=None,
                           drop_ambiguous:bool=False,
                           replace_connectors:bool=False,
                           verbose:bool=False):
    """
    Use negex to remove negated phrases from text.

    Args:
        text (str): _description_
        rules (List, optional): _description_. Defaults to None.
        drop_ambiguous (bool, optional): _description_. Defaults to False.
        replace_connectors (bool, optional): _description_. Defaults to False.
        verbose (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    if rules is None:
        with open(r'nlprules/negex_triggers.txt', encoding='utf-8') as rfile:
            rules = sortRules(rfile.readlines())

    ls_ambiguous = []
    ls_connectors = []
    for sentence in text.split('.'):
        tagger = negTagger(sentence=sentence, phrases=[],
                           rules=rules, negP=False)
        negated_phrases = tagger.getScopes()
        tagged_sentence = tagger.getNegTaggedSentence()

        if verbose:
            print(tagged_sentence)

        # use regex to get words between the tags:
        # [PSEU][PSEU], [PREP][PREP], [POSP][POSP], [PREN][PREN], [POST][POST]
        if drop_ambiguous:
            ls_ambiguous += re.findall(r'\[PSEU\](.*?)\[PSEU\]',
                                       tagged_sentence)
            ls_ambiguous += re.findall(r'\[PREP\](.*?)\[PREP\]',
                                       tagged_sentence)
            ls_ambiguous += re.findall(r'\[POSP\](.*?)\[POSP\]',
                                       tagged_sentence)
            ls_ambiguous += re.findall(r'\[PREN\](.*?)\[PREN\]',
                                       tagged_sentence)
            ls_ambiguous += re.findall(r'\[POST\](.*?)\[POST\]',
                                       tagged_sentence)
        if replace_connectors:
            ls_connectors += re.findall(r'\[CONJ\](.*?)\[CONJ\]',
                                        tagged_sentence)

        for phrase in negated_phrases:
            # remove negated phrases and phrases which introduce confusion via ambiguity
            text = text.replace(phrase, '')

    # remove ambiguous phrases
    # sort by length of phrase, so that longer phrases are removed first
    ls_ambiguous = sorted(ls_ambiguous, key=len, reverse=True)

    if drop_ambiguous:
        for phrase in ls_ambiguous:
            # sub with regex, using word boundaries
            text = re.sub(r'\b' + phrase + r'\b', '', text)

    if replace_connectors:
        for phrase in ls_connectors:
            text = re.sub(r'\b' + phrase + r'\b', '.', text)

    text = re.sub(r'\s+', ' ', text) # remove extra whitespace
    text = re.sub(r'\s+\.', '.', text) # remove spaces before full stops
    text = re.sub(r'\.+', '.', text) # remove extra full stops
    text = text.strip() # remove trainiling whitespace
    text = re.sub(r'\.$', '', text) # remove trailing full stop

    return text
