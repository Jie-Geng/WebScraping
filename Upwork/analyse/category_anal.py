from pymongo import MongoClient
import pandas as pd
from matplotlib import pyplot as plt

category_trans = {
    'Desktop Software Development': 'Web/Mobile/Software',
    'Ecommerce Development': 'Web/Mobile/Software',
    'Game Development': 'Web/Mobile/Software',
    'Mobile Development': 'Web/Mobile/Software',
    'Product Management': 'Web/Mobile/Software',
    'QA & Testing': 'Web/Mobile/Software',
    'Scripts & Utilities': 'Web/Mobile/Software',
    'Web Development': 'Web/Mobile/Software',
    'Web & Mobile Design': 'Web/Mobile/Software',
    'Other - Software Development': 'Web/Mobile/Software',
    'Database Administration': 'IT/Networking',
    'ERP / CRM Software': 'IT/Networking',
    'Information Security': 'IT/Networking',
    'Network & System Administration': 'IT/Networking',
    'Other - IT & Networking': 'IT/Networking',
    'A/B Testing': 'Data Scient/Analytics',
    'Data Visualization': 'Data Scient/Analytics',
    'Data Extraction / ETL': 'Data Scient/Analytics',
    'Data Mining & Management': 'Data Scient/Analytics',
    'Machine Learning': 'Data Scient/Analytics',
    'Quantitative Analysis': 'Data Scient/Analytics',
    'Other - Data Science & Analytics': 'Data Scient/Analytics',
    '3D Modeling & CAD': 'Engineering/Architecture',
    'Architecture': 'Engineering/Architecture',
    'Chemical Engineering': 'Engineering/Architecture',
    'Civil & Structural Engineering': 'Engineering/Architecture',
    'Contract Manufacturing': 'Engineering/Architecture',
    'Electrical Engineering': 'Engineering/Architecture',
    'Interior Design': 'Engineering/Architecture',
    'Mechanical Engineering': 'Engineering/Architecture',
    'Product Design': 'Engineering/Architecture',
    'Other - Engineering & Architecture': 'Engineering/Architecture',
    'Animation': 'Design/Creative',
    'Audio Production': 'Design/Creative',
    'Graphic Design': 'Design/Creative',
    'Illustration': 'Design/Creative',
    'Logo Design & Branding': 'Design/Creative',
    'Photography': 'Design/Creative',
    'Presentations': 'Design/Creative',
    'Video Production': 'Design/Creative',
    'Voice Talent': 'Design/Creative',
    'Other - Design & Creative': 'Design/Creative',
    'Academic Writing & Research': 'Writing',
    'Article & Blog Writing': 'Writing',
    'Copywriting': 'Writing',
    'Creative Writing': 'Writing',
    'Editing & Proofreading': 'Writing',
    'Grant Writing': 'Writing',
    'Resumes & Cover Letters': 'Writing',
    'Technical Writing': 'Writing',
    'Web Content': 'Writing',
    'Other - Writing': 'Writing',
    'General Translation': 'Translation',
    'Legal Translation': 'Translation',
    'Medical Translation': 'Translation',
    'Technical Translation': 'Translation',
    'Contract Law': 'Legal',
    'Corporate Law': 'Legal',
    'Criminal Law': 'Legal',
    'Family Law': 'Legal',
    'Intellectual Property Law': 'Legal',
    'Paralegal Services': 'Legal',
    'Other - Legal': 'Legal',
    'Data Entry': 'Admin Support',
    'Personal / Virtual Assistant': 'Admin Support',
    'Project Management': 'Admin Support',
    'Transcription': 'Admin Support',
    'Web Research': 'Admin Support',
    'Other - Admin Support': 'Admin Support',
    'Customer Service': 'Customer Service',
    'Technical Support': 'Customer Service',
    'Other - Customer Service': 'Customer Service',
    'Display Advertising': 'Sales/Marketing',
    'Email & Marketing Automation': 'Sales/Marketing',
    'Lead Generation': 'Sales/Marketing',
    'Market & Customer Research': 'Sales/Marketing',
    'Marketing Strategy': 'Sales/Marketing',
    'Public Relations': 'Sales/Marketing',
    'SEM - Search Engine Marketing': 'Sales/Marketing',
    'SEO - Search Engine Optimization': 'Sales/Marketing',
    'SMM - Social Media Marketing': 'Sales/Marketing',
    'Telemarketing & Telesales': 'Sales/Marketing',
    'Other - Sales & Marketing': 'Sales/Marketing',
    'Accounting': 'Accounting/Consulting',
    'Financial Planning': 'Accounting/Consulting',
    'Human Resources': 'Accounting/Consulting',
    'Management Consulting': 'Accounting/Consulting',
    'Other - Accounting & Consulting': 'Accounting/Consulting'
}

# load data from database
client = MongoClient()
db = client.get_database("upwork")
collection = db.freelancers

all_documents = collection.find({}, {'Category': 1, 'Country': 1, 'HourRate': 1, 'TotalEarned': 1, '_id': 0})
df = pd.DataFrame(list(all_documents))

# get big categories
df['BigCategory'] = [category_trans[c] for c in df['Category']]

# Category Distribution
grouped_df = (df.groupby('BigCategory', as_index=False)
              .agg({'HourRate': 'mean', 'TotalEarned': 'mean', 'Country': 'count'})
              .rename(columns={'HourRate': 'AvgHourRate', 'TotalEarned': 'AvgEarned', 'Country': 'Pop'}))

# draw category population
ordered = grouped_df.sort_values(by='Pop', ascending=False)
plt.figure(figsize=(10, 10))
plt.rc('font', size=10)
patches, texts = plt.pie(ordered['Pop'], shadow=False, startangle=-60)
percent = ordered['Pop']*100/ordered['Pop'].sum()
labels = ['{0} - {1:1.1f}%'.format(i, j) for i, j in zip(ordered['BigCategory'], percent)]
plt.legend(patches, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
plt.title('$10K+ Population in Categories')
plt.show()

# average earned per category
ordered = grouped_df.sort_values(by='AvgEarned', ascending=False)
plt.figure(figsize=(10, 6))
plt.rc('font', size=10)
plt.bar(ordered['BigCategory'], ordered['AvgEarned'])
plt.xticks(rotation='vertical')
plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
plt.rc('font', size=10)
plt.title('Average Earned in Categories')
plt.ylabel('Average Earned(K$)')
plt.show()
