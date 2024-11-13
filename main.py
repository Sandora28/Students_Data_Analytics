import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import seaborn as sns
import zipfile

# opening zip and reading csv file
with zipfile.ZipFile('event_data_train.zip') as z:
    with z.open('event_data_train.csv') as f:
        event_data = pd.read_csv(f)
# loads the data from csv into dataframes
submissions_data = pd.read_csv("submissions_data_train.csv")

# converting timestamps to real datetime
event_data["timestamp"] = pd.to_datetime(event_data["timestamp"], unit='s')
submissions_data["timestamp"] = pd.to_datetime(submissions_data["timestamp"], unit='s')


# function for merging data from two different tables into one
def merge_data(event_data, submissions_data):
    merged_data = pd.merge(event_data[:10000], submissions_data[:5000], on='user_id', how='left')
    return merged_data

# create new dataframe with existed function
merged_data = merge_data(event_data, submissions_data)


# function for calculating , counting specific columns grouped by desired column
def user_stats(event_data, submissions_data):
    user_actions = event_data.groupby('user_id')['action'].count().reset_index(name='_total_actions')

    correct_submissions = submissions_data[submissions_data['submission_status'] == 'correct'] \
        .groupby('user_id')['submission_status'].count().reset_index(name='_correct_submissions')

    engagement_time = event_data.groupby('user_id').agg(
        first_action=('timestamp', 'min'),
        last_action=('timestamp', 'max')
    )

    total_submissions = submissions_data.groupby('user_id')['submission_status'].count().reset_index(
        name='_total_submissions')

    return user_actions, correct_submissions, engagement_time, total_submissions


user_actions, correct_submissions, engagement_time, total_submissions = user_stats(event_data,submissions_data)

# merge aggregated and counted data into a dataset
merged_data = pd.merge(merged_data, user_actions, on='user_id', how='left')
merged_data = pd.merge(merged_data, correct_submissions, on='user_id', how='left')
merged_data = pd.merge(merged_data, engagement_time[['first_action', 'last_action']], on='user_id', how='left')
merged_data = pd.merge(merged_data, total_submissions, on='user_id', how='left')

# calculating engagement duration in days
merged_data['engagement_duration'] = (merged_data['last_action'] - merged_data['first_action']).dt.days

# calculate correct submission ratio based on total submissions and correct submissions
merged_data['correct_submission_ratio'] = merged_data['_correct_submissions'] / merged_data['_total_submissions']

# filling all nan value with 0
merged_data.fillna(0, inplace=True)

# starting connection to sqlite for saving cleaned , distilled data.
conn = sqlite3.connect('student_db.db')

reduced_data = merged_data.groupby('user_id').agg({
    'action': 'count',
    '_correct_submissions': 'sum',
    '_total_submissions': 'sum',
    'first_action': 'min',
    'last_action': 'max',
    'engagement_duration': 'mean',
    'correct_submission_ratio': 'mean'
}).reset_index()

# convert datetime to string for sqlite compatibility
reduced_data['first_action'] = reduced_data['first_action'].astype(str)
reduced_data['last_action'] = reduced_data['last_action'].astype(str)

# inserting data into sqlite
reduced_data.to_sql('students_data', conn, if_exists='replace', index=False)

# sqlite query: return students with the highest correct submission ratio
query = "SELECT user_id, correct_submission_ratio FROM students_data ORDER BY correct_submission_ratio DESC LIMIT 20"
result = pd.read_sql_query(query, conn)
print(result)


conn.close()

# defining thresholds for user profiles , that is used in a user_profile function
high_engagement_threshold = reduced_data['engagement_duration'].median()
high_accuracy_threshold = reduced_data['correct_submission_ratio'].median()


# based on engagement duration and correct submission ratio returning student performance
def student_performance(row):
    if row['engagement_duration'] > high_engagement_threshold and row[
        'correct_submission_ratio'] > high_accuracy_threshold:
        return 'High Engagement & High Accuracy'
    elif row['engagement_duration'] > high_engagement_threshold and row[
        'correct_submission_ratio'] <= high_accuracy_threshold:
        return 'High Engagement & Low Accuracy'
    elif row['engagement_duration'] <= high_engagement_threshold and row[
        'correct_submission_ratio'] > high_accuracy_threshold:
        return 'Low Engagement & High Accuracy'
    else:
        return 'Low Engagement & Low Accuracy'


# apply classification based on function criteria
reduced_data['student_performance'] = reduced_data.apply(student_performance, axis=1)

# using countplot for counting and graphing number of students based on  performances(criteria)
plt.figure(figsize=(10, 6))
sns.countplot(x='student_performance', data=reduced_data, palette='Set2')
plt.title('Student Performances Based on Engagement Duration and Correct Submission Ratio', fontsize=16)
plt.xlabel('Student Performance', fontsize=14)
plt.ylabel('Count of Users', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.tight_layout()
plt.show()

#  Engagement Duration vs Correct Submission Ratio
plt.figure(figsize=(10, 6))
sns.scatterplot(x='engagement_duration', y='correct_submission_ratio', hue='student_performance', data=reduced_data,
                palette='Set1', s=100)
plt.title('Engagement Duration vs Correct Submission Ratio', fontsize=16)
plt.xlabel('Engagement Duration (days)', fontsize=14)
plt.ylabel('Correct Submission Ratio', fontsize=14)
plt.tight_layout()
plt.show()


# handle outliers in engagement duration by setting a threshold
threshold = reduced_data['engagement_duration'].quantile(0.80)
reduced_data['engagement_duration'] = reduced_data['engagement_duration'].apply(lambda x: min(x, threshold))

# save the final cleaned data to csv
reduced_data.to_csv('student_profiles.csv', index=False)
