import os
import shutil
import logging
import datetime
import pandas
import tarfile
import json
import re
from typing import Dict

logging.basicConfig(filename=r'C:\Users\t_p_c\OneDrive\Documents\GitHub\MathsDataset\Data\logs\move_file.log', level=logging.ERROR)

def read_into_dict(path, train_or_test) -> Dict:
    """
    Load all .json files in a directory and its subdirectories into a dictionary.

    Parameters:
    path (str): The path to the directory to be loaded.
    train_or_test (str): The name of the subdirectory to be ignored.

    Returns:
    Dict: A dictionary with subdirectory names as keys and lists of dictionaries as values,
    each representing a .json file.
    """
    train_data = {}
    try:
        for dirpath, subdirs, files in os.walk(path):
            subdirs_data = []
            for file in files:
                if file.endswith(".json"):
                    with open(os.path.join(dirpath, file)) as f:
                        subdirs_data.append(json.load(f))
            if dirpath.split("\\")[-1] != train_or_test:
                train_data[dirpath.split("\\")[-1]] = subdirs_data
    except Exception as e:
        logging.error(
            f"An error occured while attempting to read the file ito a dictionary {path}: {e}. {datetime.datetime.now()}"
        )
    return train_data

def move_file(
    source,
    destination_dir,
    logging_dst=r"C:\Users\t_p_c\OneDrive\Documents\GitHub\MathsDataset\Data\logs\move_file.log",
):
    """
    This function moves a file from the source to the destination directory, while ensuring that a file with the same name does not exist in the destination directory.
    If a file with the same name exists, it will rename the file by appending a number to the end of the file name.
    The function will log any error that occurs during the move process in the specified log file.

    Parameters:
        source (str): The source file path to move.
        destination_dir (str): The destination directory path to move the file to.
        logging_dst (str, optional): The log file path. Defaults to 'C:/Users/t_p_c/OneDrive/Documents/GitHub/MathsDataset/Data/logs/move_file.log'.

    Returns:
        bool: True if the move was successful, False otherwise.
    """
    # logging.basicConfig(filename=logging_dst, level=logging.ERROR)

    if not os.path.exists(source):
        logging.error(f"File not found at source. {datetime.datetime.now()}")
        return False

    destination_file_name = "/".join([destination_dir, os.path.basename(source)])

    if os.path.exists(destination_file_name):
        base, ext = os.path.splitext(destination_file_name)
        try:
            i = 0
            while os.path.exists(f"{base}_{i}{ext}"):
                i += 1
            destination_file_name = f"{base}_{i}{ext}"
        except Exception as e:
            logging.error(
                f"An error occured while attempting to rename the file {destination_file_name}: {e}. {datetime.datetime.now()}"
            )

    try:
        shutil.move(src=source, dst=destination_file_name)
    except Exception as e:
        logging.error(
            f"An error occured while attempting to move the file {source} to {destination_file_name}: {e}. {datetime.datetime.now()}"
        )
        return False

    return True


def move_files_in_folder(
    source_dir=r"C:\Users\t_p_c\DataEng\Beginner Challenges",
    destination_dir=r"C:\Users\t_p_c\OneDrive\Documents\GitHub\MathsDataset\Data\incoming",
    logging_dst=r"C:\Users\t_p_c\OneDrive\Documents\GitHub\MathsDataset\Data\logs\move_file.log",
):
    """
    This function moves all files in a given source directory to a specified destination directory, while logging any errors that occur during the move process in the specified log file.

    Parameters:
        source_dir (str, optional): The source directory to move files from. Defaults to r'C:/Users/t_p_c/DataEng/Beginner Challenges'.
        destination_dir (str, optional): The destination directory to move files to. Defaults to r'C:/Users/t_p_c/OneDrive/Documents/GitHub/MathsDataset/Data/incoming'.
        logging_dst (str, optional): The log file path. Defaults to r'C:/Users/t_p_c/OneDrive/Documents/GitHub/MathsDataset/Data/logs/move_file.log'.

    Returns:
        bool: True if all files in the source directory were moved successfully, False otherwise.
    """
    # logging.basicConfig(filename=logging_dst, level=logging.ERROR)
    if os.path.exists(source_dir):
        try:
            if os.listdir(source_dir):
                for file in os.listdir(source_dir):
                    source_file = os.path.join(source_dir, file)
                    if os.path.isfile(source_file):
                        move_file(source_file, destination_dir)
            else:
                logging.error(f"Source directiory is empty. {datetime.datetime.now()}")
                return False
        except Exception as e:
            logging.error(
                f"An error occured while attempting to scan the source folder for incoming files, {e}. {datetime.datetime.now()}"
            )
            return False
    else:
        logging.error(f"Source directory not found. {datetime.datetime.now()}")
        return False
    return True

"""""""     Pre-processing  """""""

def parse_final_answer(sample, first_match="\\\boxed", second_match="\\fbox"):
    """
    Find the final answer in a math problem text.
    
    Parameters:
        sample (tuple): A tuple containing two strings. The first string is a math problem statement and the second string is a solution to the problem.
        to_match (str, optional): A regular expression pattern used to match the final answer in the solution text. Defaults to r"\\boxed{(.*?)}".
    
    Returns:
        list: A list of matches found by the regular expression.
    
    Example:
        >>> test_sample = ('If $x = 2$ and $y = 5$, then what is the value of $\\frac{x^4+2y^2}{6}$ ?',
        ... 'We have  \\[\\frac{x^4 + 2y^2}{6} = \\frac{2^4 + 2(5^2)}{6} = \\frac{16+2(25)}{6} = \\frac{16+50}{6} = \\frac{66}{6} = \\boxed{11}.\\]')
        >>> find_final_answer(sample=test_sample)
        ['11']
    """
    q, a = sample
    match = a.rfind(first_match)
    if match < 0:
        match = a.rfind(second_match)

    ind = match + 1
    num_left_braces_open = 0
    right_brace_ind = 0
    while ind < len(a):
        if a[ind] == '{':
            num_left_braces_open += 1
        elif a[ind] == '}':
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_ind = ind
                break
        ind+=1
    
    to_extract = a[match+1:right_brace_ind+1]
    
    return to_extract

def multi_split(s, splitters):
    """
    Split a string into substrings using multiple separators.
    
    Parameters:
        s (str): The string to be split.
        splitters (list): A list of strings used as separators.
    
    Returns:
        list: A list of substrings from the input string, split using the given separators.
    
    Example:
        >>> test_string = 'frac{1}{x}+'
        >>> test_splitters = ['{', '}', '+']
        >>> multi_split(s=test_string, splitters=test_splitters)
        ['frac', '1', 'x', '+']
    """
    split_regex = '|'.join(map(re.escape, splitters))
    return re.split(split_regex, s)

def parse_questions(question, stopwords, splitters=['\\', '$', '&', ' ', '?'], punctuation_pattern = '[,.!?;:]'):
    """
    Parse a math problem statement and return a list of filtered and cleaned tokens.
    
    Parameters:
        question (str): A string containing the math problem statement.
        stopwords (list): A list of stopwords to be removed from the question.
        splitters (list, optional): A list of strings to split the question string by. Defaults to ['\\', '$', '&', ' ', '?'].
        punctuation_pattern (str, optional): A regular expression pattern for punctuation. Defaults to '[,.!?;:]'.
        
    Returns:
        list: A list of filtered and cleaned tokens from the question string.
        
    Example:
        >>> test_question = 'What is the value of $\\frac{x^4+2y^2}{6}$ ?'
        >>> parse_questions(question=test_question)
        ['value', 'frac', 'x^4', '2y^2', '6']
    """
    question = question.lower()
    question_tokens = multi_split(question, splitters)
    expression = [i for i in question_tokens if i not in stopwords]
    expression = [re.sub(r'\s+', ' ', i) for i in expression]
    expression = [re.sub(punctuation_pattern, '', i).strip() for i in expression]
    expression = [i for i in expression if i != '']
    
    return expression

def preprocess(data, stopwords, levels={'1','2','3','4','5','?'}):
    """
    Preprocess the data to separate samples by difficulty level.
    
    Parameters:
        data (dict): A dictionary containing fields as keys and samples as values.
        stopwords (list): A list of stopwords to be removed from the question.
        levels (set, optional): A set of strings specifying the difficulty levels. Defaults to {'1','2','3','4','5','?'}.
    
    Returns:
        dict: A dictionary containing preprocessed data separated by difficulty level.
    
    Example:
        >>> test_data = {'field_1': [{'problem': 'If x = 2 and y = 5, then what is the value of \\frac{x^4+2y^2}{6} ?',
        ...                           'solution': 'We have  \\[\\frac{x^4 + 2y^2}{6} = \\frac{2^4 + 2(5^2)}{6} = \\frac{16+2(25)}{6} = \\frac{16+50}{6} = \\frac{66}{6} = \\boxed{11}.\\]',
        ...                           'level': 'Level 1'},
        ...                          {'problem': 'If x = 2 and y = 5, then what is the value of \\frac{x^4+2y^2}{6} ?',
        ...                           'solution': 'We have  \\[\\frac{x^4 + 2y^2}{6} = \\frac{2^4 + 2(5^2)}{6} = \\frac{16+2(25)}{6} = \\frac{16+50}{6} = \\frac{66}{6} = \\boxed{11}.\\]',
        ...                           'level': 'Level 2'}],
        ...            'field_2': [{'problem': 'If x = 2 and y = 5, then what is the value of \\frac{x^4+2y^2}{6} ?',
        ...                        'solution': 'We have  \\[\\frac{x^4 + 2y^2}{6} = \\frac{2^4 + 2(5^2)}{6} = \\frac{16+2(25)}{6} = \\frac{16+50}{6} = \\frac{66}{6} = \\boxed{11}.\\]',
        ...                        'level': 'Level 1'}]}
        >>> preprocess(data=test_data)
        {'field_1': {'1': [(['If', 'x', '2', 'y', '5', 'value', 'x^4', '2y^2', '6'], '11')], 
                     '2': [(['If', 'x', '2', 'y', '5', 'value', 'x^4', '2y^2', '6'], '11')]},
         'field_2': {'1': [(['If', 'x', '2', 'y', '5', 'value', 'x^4', '2y^2', '6'], '11')]}}
    """
    preprocessed_data = {}
    for field, samples in data.items():
        field_by_levels = {}
        for level in levels:
            field_by_levels[level] = [(parse_questions(i['problem'], stopwords), i['solution']) for i in samples if i['level'].split(" ")[-1] == level]
        preprocessed_data[field] = {level: [(i[0], parse_final_answer(i)) for i in samples] for level, samples in field_by_levels.items()}
    
    return preprocessed_data

def reformat_fractions(expr, fraction_pattern = r"frac{ (.*?)}{(.*?)}") -> str:
    """
    Reformats fractions in a mathematical expression.
    
    Parameters:
    - expr (str): The mathematical expression to reformat.
    - fraction_pattern (str, optional): The regular expression pattern to use for identifying fractions. Default is r"\\frac{(.*?)}{(.*?)}".
    
    Returns:
    - str: The reformed expression with the fractions formatted as 'frac(numerator/denominator)'.
    
    Example:
    >>> reformat_fractions("$x = 2$ and $y = 5$, then what is the value of $\frac{x^4+2y^2}{6}$ ?")
    '$x = 2$ and $y = 5$, then what is the value of $\frac{x^4+2y^2}{6}$ ?'
    """
    expr = re.sub(fraction_pattern, r"frac(\1/\2)", expr)
    
    return expr

def format_arrays(expression, arr_patterns=['begin{array}{ccc}', 'begin{array}{cl}'], end_arr_pattern='end{array}'):
    """
    Format math arrays in a list of expressions.
    
    Parameters:
        expression (list): A list of strings containing expressions.
        arr_patterns (list, optional): A list of strings that represent the starting pattern of math arrays. Defaults to ['begin{array}{ccc}', 'begin{array}{cl}'].
        end_arr_pattern (str, optional): A string that represents the end pattern of a math array. Defaults to 'end{array}'.
        
    Returns:
        list: A list of strings with the math arrays formatted.
    
    Example:
        >>> expression = ['A matrix with three rows and two columns: \\begin{array}{ccc} 1 & 2 \\ 3 & 4 \\ 5 & 6 \\end{array}']
        >>> format_arrays(expression)
        ['A matrix with three rows and two columns: array[1 & 2 \\ 3 & 4 \\ 5 & 6 ]']
    """
    for i in arr_patterns:
        expression = [re.sub(i, r"array[", j) for j in expression]
    expression = [re.sub(end_arr_pattern, r"]", i) for i in expression]
    return expression