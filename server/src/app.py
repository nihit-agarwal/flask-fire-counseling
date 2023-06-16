# Importing modules for web development and using other helper modules
from flask import Flask, render_template, request
import backend as bk
import os

# Creating a new app object
app = Flask(__name__)


@app.route('/')
def landing_form():
    """
    Function to access information from 2022 data to display options in form.
    :return: rendered landing page for flask to display
    """
    # Reading 2022 data file
    main_df = bk.main_df
    categories = list(main_df['Category'].unique())
    # Courses to pick as preference
    courses_df = main_df[['Branch', 'branch_ins']]
    courses_df['Code'] = courses_df.apply(lambda row: row.branch_ins[3:], axis=1)
    courses_df = courses_df[['Branch', 'Code']].sort_values('Branch')
    courses = list(set(courses_df.itertuples(index=False, name=None)))
    courses.sort(key=lambda x: x[0])
    courses.insert(0, ("No preference", "0"))
    # Colleges to pick as preference
    colleges_df = main_df[['College', 'branch_ins']]
    colleges_df['Code'] = colleges_df.apply(lambda row: row.branch_ins[:3], axis=1)
    colleges = list(set(colleges_df[['College', 'Code']].itertuples(index=False, name=None)))
    colleges.insert(0, ["No preference", "0"])
    # Index labels to act as name attribute for value recall
    branch_indices = ["branch" + str(i) for i in range(1, 6)]
    college_indices = ["college" + str(i) for i in range(1, 6)]
    return render_template('index.html', courses=courses, colleges=colleges, b_indices=branch_indices,
                           c_indices=college_indices, categories=categories)


@app.route('/options', methods=['POST'])
def results_render():
    """
    Function to process form input and return useful results
    :return: rendered results HTML file for display
    """
    # Acquiring course and college preferences from form
    courses = [request.form.get("branch" + str(i)) for i in range(1, 6)]
    colleges = [request.form.get("college" + str(i)) for i in range(1, 6)]
    # Acquiring all possible ranks of user - number or None
    ranks = list()
    rank = request.form['crlRank']
    ranks.append(int(rank) if rank != '' else None)
    rank = request.form['catRank']
    ranks.append(int(rank) if rank != '' else None)
    rank = request.form['pRank']
    ranks.append(int(rank) if rank != '' else None)
    # Acquiring user category - one of the ten options
    category = request.form['category']
    # Acquiring user gender -  N or F
    gender = request.form['Gender']
    # Determining possible options for user using 2022 dataset and backend algorithms
    base_options = bk.find_options()
    # Calculating probability for each option using survival function
    options_with_probs = bk.find_probabilities(base_options, ranks, gender, category)
    # Ordering options using median as score
    def_order = bk.default_order(options_with_probs)
    # Ordering options using user preference also
    cust_order = bk.custom_order(def_order, courses, colleges)
    return render_template('result.html', options=def_order, sList=cust_order)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))