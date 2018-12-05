from pymongo import MongoClient
import pandas as pd
from collections import Counter
from matplotlib import pyplot as plt


client = MongoClient()
db = client.get_database("upwork")
collection = db.freelancers

all_documents = collection.find({}, {'profile_id': 0, '_id': 0})
df = pd.DataFrame(list(all_documents))

skill_list = [item for sublist in df.Skills for item in sublist]
skill_usage = dict(Counter(skill_list))

reverse_sorted = sorted(skill_usage.items(), key=lambda x: x[1], reverse=True)
skill_df = pd.DataFrame(reverse_sorted)
skill_df.columns = ['skill', 'usage']

# get top 20 common skills
top_skills = skill_df[:20][:]

# draw top 20 skills
plt.figure(figsize=(10, 5))
plt.bar(top_skills.skill, top_skills.usage)
plt.title('Top 20 skills used by Upwork $10k+ freelancers')
plt.xticks(rotation='vertical')
plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
plt.show()
