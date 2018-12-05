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

# load data from the database
client = MongoClient()
db = client.get_database("upwork")
collection = db.freelancers

all_documents = collection.find({}, {"_id": 0})
df = pd.DataFrame(list(all_documents))

# get big categories
df['BigCategory'] = [category_trans[c] for c in df['Category']]


def hour_rate_per_category(data_frame, country=''):
    # aggregate and sort
    g_df = data_frame.groupby('BigCategory')['HourRate'].agg([pd.np.min, pd.np.mean, pd.np.max, pd.np.std])
    by_hour = g_df.sort_values(by='mean', ascending=False)
    by_hour = by_hour.reset_index()

    # draw plot
    plt.bar(by_hour['BigCategory'], by_hour['mean'], yerr=by_hour['std'], align='center', alpha=0.5)
    plt.xticks(rotation='vertical')
    plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
    plt.rc('font', size=10)
    country_label = ''
    if country != '':
        country_label = '(' + country + ')'
    plt.title('Hourly Rate in Categories' + country_label)
    plt.ylabel('Hourly Rate ($/h)')
    plt.show()


# global chart
hour_rate_per_category(df)

countries = ['United States', 'Philippines', 'India', 'Bangladesh', 'Pakistan', 'Ukraine', 'Russia', 'United Kingdom',
             'Serbia', 'Canada']

for c in countries:
    hour_rate_per_category(df[df['Country'] == c], c)

# histogram of hour rate
histogram = df[df['HourRate'] < 200]
plt.hist(histogram['HourRate'], bins=50, rwidth=0.85)
plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
plt.rc('font', size=10)
plt.title('Histogram of Hourly Rate')
plt.xlabel('Hourly Rate ($/h)')
plt.ylabel('Population')
plt.axvline([df['HourRate'].mean()], linestyle='--', color='red')  # vertical lines
plt.show()

# mean rate
print("Mean Hourly Rate is " + str(round(df['HourRate'].mean(), 2)) + "$/h")

# min rate freelancers
print(df[df['HourRate'] == df['HourRate'].min()])

# max rate freelancers
print(df[df['HourRate'] == df['HourRate'].max()])


# hour rate per country
filtered_df = df[df['Country'].isin(countries)]
grouped_df = filtered_df.groupby('Country')['HourRate'].agg([pd.np.min, pd.np.mean, pd.np.max, pd.np.std])
by_country = grouped_df.sort_values(by='mean', ascending=False)
by_country = by_country.reset_index()

# draw plot
plt.bar(by_country['Country'], by_country['mean'], yerr=by_country['std'], align='center', alpha=0.5)
plt.xticks(rotation='vertical')
plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
plt.rc('font', size=14)
plt.title('Hourly Rates in Top 10 Countries')
plt.ylabel('Hourly Rate ($/h)')
plt.show()
