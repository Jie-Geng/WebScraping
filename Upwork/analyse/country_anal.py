from pymongo import MongoClient
import pandas as pd
from matplotlib import pyplot as plt

client = MongoClient()
db = client.get_database("upwork")
collection = db.freelancers

# filter data from mongo db
all_documents = collection.find({}, {'City': 1, 'Country': 1, 'TotalEarned': 1, '_id': 0})
df = pd.DataFrame(list(all_documents))

# convert the type of TotalEarned from string to integer
df['TotalEarned'] = df['TotalEarned'].astype('int64')

# group by country
grouped_df = df.groupby('Country').agg({'TotalEarned': ['sum', 'mean', 'count']})
grouped_df.columns = [col[1] for col in grouped_df.columns]
grouped_df = grouped_df.reset_index()

# top 10 population countries
pop_ordered = grouped_df.sort_values(by='count', ascending=False)[:][:]

plt.figure(figsize=(10, 5))
plt.bar(pop_ordered['Country'][:10], pop_ordered['count'][:10])
plt.xticks(rotation='vertical')
plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
plt.rc('font', size=10)
plt.title('Top 10 Countries - $10K+ Freelancer Population')
plt.ylabel('Freelancers Population')
plt.show()

explode = [0.0 for x in range(11)]
explode[0] = 0.05

show_pop = pop_ordered[:][:10]
show_pop.loc[10] = ['Others', pop_ordered['sum'][10:].sum(), 0, pop_ordered['count'][10:].sum()]

plt.figure(figsize=(10, 10))
plt.rc('font', size=10)
plt.pie(show_pop['count'][:], explode=explode, labels=show_pop['Country'][:], autopct='%1.1f%%', shadow=False,
        startangle=90)
plt.title('Top 10 - Upwork $10K+ Freelancer Population')
plt.show()

top_10 = pop_ordered[:][:10]
top_10 = top_10.sort_values(by='mean', ascending=False)

plt.figure(figsize=(10, 5))
plt.bar(top_10['Country'], top_10['mean'])
plt.xticks(rotation='vertical')
plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
plt.rc('font', size=10)
plt.title('Top 10 Countries - Average Earned')
plt.ylabel('Average Earned($1K)')
plt.show()

# the most sparse countries
print(pop_ordered[pop_ordered['count'] < 2].Country)
# Tanzania, Bahamas, Bermuda, Macao, Reunion, Cayman Islands, Somalia, Haiti, Micronesia, \
# Monaco, Liechtenstein, Guinea, Mozambique, Namibia, Guam, Netherlands Antilles, Iceland, Curacao,
# Saint Kitts and Nevis, Saint Vincent and the Grenadines, Sierra Leone, Congo, Jersey
