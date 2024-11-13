Student Performance Analysis ---
This project analyzes student engagement and submission accuracy based on event and submission data. The analysis focuses on:

Engagement Duration: The time span from the student's first to last recorded action.
Correct Submission Ratio: The proportion of correct submissions to total submissions.
Student Performance Classification: Students are classified into performance categories based on engagement duration and correct submission ratio.
Features
Merging Data: Combines event and submission data to create a detailed dataset.
Calculations: Computes metrics like engagement duration, correct submission ratio, and aggregates key stats for each student.
Visualization: Uses graphs to display student performance and correlations between engagement and accuracy.
Outlier Handling: Trims engagement duration outliers to the 80th percentile.
Database Integration: Saves reduced data into an SQLite database for queries and further analysis.
Data Sources
You will not find the file event_data_train.csv in this repository because it's too large for GitHub. However, you can download it from the following link:

Download event_data_train.csv from here <!-- (https://www.kaggle.com/datasets/kapturovalexander/predict-students-drop-out-of-the-course/data?select=event_data_train.csv) -->

---How to Set Up:
1. Download event_data_train.csv from the link above.
2. Place the event_data_train.csv file in the root directory of this project and zip it.
3. Ensure submissions_data_train.csv is also in the root directory. ---

Prerequisites
Python 3.x
Pandas, Seaborn, Matplotlib
SQLite3
