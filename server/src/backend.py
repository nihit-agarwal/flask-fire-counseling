# Importing required modules for data reading
import copy
import math
import pickle
from typing import List, Any

import lifelines
import pandas as pd


# This module contains functions to test backend work using 2022 data.


def initialization():
    m_df = pd.read_csv('Data/2022_Data_v2.csv')
    m_df = m_df.iloc[:, 1:]
    df = pd.read_csv('Data/Median_order.csv')
    df = df.iloc[:, 1:]
    df.columns = ['branch_ins', 'median', 'College', 'Branch']
    med_order = df[['branch_ins', 'median']].itertuples(index=False, name=None)
    med_order = list(med_order)
    return m_df, med_order


main_df, order = initialization()


def find_options():
    """
    Function ot retrieve unique options
    :return: list of lists of format (College, Branch, branch_ins code)
    """
    # Unique list of options extracted
    sub_df = main_df[(main_df['Category'] == 'OPEN') & (main_df['Gender'] == 'N')][['College','Branch','branch_ins']]
    options_tup = sub_df.itertuples(index=False, name=None)
    options: list[list[Any] | Any] = list(options_tup)
    # Converting list of tuples to list of lists for mutability
    for i in range(len(options)):
        options[i] = list(options[i])
    return options


def find_probabilities(options: list, ranks: list, gender: str, category: str):
    """
    Function to calculate probability of seat survival for given rank
    :param options: List of options generated based on closing ranks
    :param ranks: user ranks of three types
    :param gender: user gender
    :param category: user category
    :return: list of options extended with [probability, range of probabilities alpha=0.15] where the largest
             probability is considered
    """
    # Creating categories to try out
    categories = ['OPEN', category.replace(' (PwD)', ''), category]
    for opt_num in range(len(options)):
        max_prob = -1
        lower = 0
        upper = 0
        for i in range(3):
            rank = ranks[i]
            if rank:
                case = options[opt_num][2]
                try:
                    probability = survival_predict('N', case, rank, categories[i])
                except Exception as error:
                    probability = -1
                    print(error, case, 'N')
                if probability != -1:
                    if probability[0] > max_prob:
                        max_prob = probability[0]
                        lower = probability[1]
                        upper = probability[2]
                if gender == 'F':
                    try:
                        probability = survival_predict('F', case, rank, categories[i])
                    except Exception as error:
                        probability = -1
                        print(error, case, 'F')
                    if probability != -1:
                        if probability[0] > max_prob:
                            max_prob = probability[0]
                            lower = probability[1]
                            upper = probability[2]
        options[opt_num].extend([str(round(max_prob, 3)), (str(round(lower, 3)), str(round(upper, 3)))])
    return options


def default_order(options: list):
    """
    Function to order available options in order of median (parameter to show order of branch-ins)
    :param options: list of possible branch institute combinations with probabilities
    :return: list of options with appended median as score in default order using 2022 preferences
    """
    # New ordered options
    result = []
    for i, v in order:
        for j in options:
            if i == j[2]:
                j.append(v)
                result.append(j)
                break
    return result


def custom_order(options: list, branches: list, colleges: list):
    """
    Function to customize order of options based on user preferences
    :param options: List of all options with median score
    :param branches: user preferred top 5 branches
    :param colleges: user preferred top 5 colleges
    :return: a new ordered list based on preferences
    """
    b_options = copy.deepcopy(options)
    # for opt in b_options:
    #     opt.append('')
    score = 0.1
    for i in colleges:
        if i == '':
            continue
        for j in range(len(b_options)):
            if i == b_options[j][2][:3]:
                b_options[j][5] = b_options[j][5] * score
                # b_options[j][-1] = '*'
                b_options[j][0] += ' **'
        score += 0.1

    score = 0.5

    for i in branches:
        if i == '':
            continue
        for j in range(len(b_options)):
            if i == b_options[j][2][3:]:
                b_options[j][5] *= score
                # if b_options[j][-1] == '*':
                #     b_options[j][-1] = '*#'
                # elif not b_options[j][-1]:
                #     b_options[j][-1] = '#'
                b_options[j][1] += ' **'
        score += 0.1

    b_options.sort(key=lambda x: x[5])

    for i in range(len(b_options)):
        p = float(b_options[i][3])
        color = None
        if p <= 0.25:
            color = None
        elif p <= 0.5:
            color = 'pistachio'
        elif p <= 0.75:
            color = 'mint'
        else:
            color = 'chartreuse'
        b_options[i].append(color)
    return b_options


def survival_predict(gender, case, rank, category):
    """
    Helper function to calculate probability of seat survival at given rank
    :param gender: Gender of user to choose right dataset
    :param case: branch institute combination to check for
    :param rank: Rank of user in given category
    :param category: Category to use for dataset
    :return: tuple of (survival probability, lower bound, upper bound)
    """
    fname = f'{gender}-{case}-{category}'
    file = open(f'Data/probExp/{fname}', 'rb')
    try:
        kmf = pickle.load(file)
    except:
        return -1
    survival_prob = kmf.predict(rank)
    if type(kmf) == lifelines.fitters.exponential_fitter.ExponentialFitter:
        ll = kmf.summary['coef lower 95%'][0]
        ul = kmf.summary['coef upper 95%'][0]
        lower = round(math.exp(-1 * rank / ll), 3)
        upper = round(math.exp(-1 * rank / ul), 3)
        if lower > 1.0:
            lower = survival_prob
    else:
        file = open(f'Data/prob/{fname}', 'rb')
        kmf = pickle.load(file)
        conf_df = kmf.confidence_interval_survival_function_
        lower = conf_df[conf_df.index <= rank].iloc[-1, 0]  # ['N_lower_0.95']
        upper = conf_df[conf_df.index <= rank].iloc[-1, 1]  # ['N_upper_0.95']

    return survival_prob, lower, upper
