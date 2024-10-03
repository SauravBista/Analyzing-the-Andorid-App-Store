# Import Libraries
import pandas as pd
import plotly.express as px

# Show numeric output in decimal format e.g., 2.15
pd.options.display.float_format = '{:,.2f}'.format

# Read the Dataset
df_apps = pd.read_csv('apps.csv')

# Data Cleaning
# 1. Checking the shape (rows, columns) and a sample of the dataset
print(df_apps.shape)  # (10841, 12)
df_apps.sample(5)

# 2. Dropping unused columns: 'Last_Updated' and 'Android_Version'
df_apps = df_apps.drop(['Last_Updated', 'Android_Ver'], axis=1)

# 3. Handling NaN values in 'Rating' column and cleaning the data
df_apps['Rating'].isna().sum()  # Total rows with NaN values in Rating: 1474
df_apps_clean = df_apps.dropna()
print(df_apps_clean.shape)  # (9367, 10)

# 4. Checking and removing duplicates
duplicated_rows = df_apps_clean[df_apps_clean.duplicated()]
print(duplicated_rows.shape)  # (476, 10)

# Checking duplicate entries for the "Instagram" app
df_apps_clean[df_apps_clean.App == 'Instagram']

# Dropping duplicates based on 'App', 'Type', and 'Price'
df_apps_clean = df_apps_clean.drop_duplicates(subset=['App', 'Type', 'Price'])
df_apps_clean[df_apps_clean.App == 'Instagram']
print(df_apps_clean.shape)  # (8199, 10)

# 5. Finding the highest-rated apps
df_apps_clean.sort_values('Rating', ascending=False).head()

# 6. Finding the 5 largest apps in terms of size (MBs)
df_apps_clean.sort_values('Size_MBs', ascending=False).head()

# 7. Finding the 5 apps with the most reviews
df_apps_clean.sort_values('Reviews', ascending=False).head(50)

# Visualizing Content Ratings with Pie and Donut Charts
ratings = df_apps_clean.Content_Rating.value_counts()
fig = px.pie(labels=ratings.index, values=ratings.values, title='Content Rating', hole=0.6, names=ratings.index)
fig.update_traces(textposition='outside', textinfo='percent+label')
fig.show()

# Numeric Type Conversion: Examine the Number of Installs
# 8. Checking how many apps have over 1 billion installs, or just a single install
df_apps_clean['Installs'].describe()
df_apps_clean[['App', 'Installs']].groupby('Installs').count()

# Converting 'Installs' column to numeric
df_apps_clean.Installs = df_apps_clean.Installs.astype(str).str.replace(',', "")
df_apps_clean.Installs = pd.to_numeric(df_apps_clean.Installs)
df_apps_clean[['App', 'Installs']].groupby('Installs').count()

# Converting 'Price' column to numeric
df_apps_clean.Price = df_apps_clean.Price.astype(str).str.replace('$', "")
df_apps_clean.Price = pd.to_numeric(df_apps_clean.Price)
df_apps_clean.Price.describe()

# 9. Finding the most expensive apps and filtering out junk
df_apps_clean.sort_values('Price', ascending=False).head(20)
df_apps_clean = df_apps_clean[df_apps_clean['Price'] < 250]
df_apps_clean.sort_values('Price', ascending=False).head(5)

# 10. Calculating highest grossing paid apps (Revenue Estimate)
df_apps_clean['Revenue_Estimate'] = df_apps_clean.Installs.mul(df_apps_clean.Price)
df_apps_clean.sort_values('Revenue_Estimate', ascending=False)[:10]

# 11. Number of unique categories
df_apps_clean.Category.nunique()  # 33
top10_category = df_apps_clean.Category.value_counts()[:10]
top10_category

# Vertical Bar Chart - Highest Competition (Number of Apps)
bar = px.bar(x=top10_category.index, y=top10_category.values)
bar.show()

# Horizontal Bar Chart - Most Popular Categories (Highest Downloads)
category_installs = df_apps_clean.groupby('Category').agg({'Installs': pd.Series.sum})
category_installs.sort_values('Installs', ascending=True, inplace=True)

h_bar = px.bar(x=category_installs.Installs, y=category_installs.index, orientation='h', title='Category Popularity')
h_bar.update_layout(xaxis_title='Number of Downloads', yaxis_title='Category')
h_bar.show()

# Category Concentration - Downloads vs. Competition
cat_number = df_apps_clean.groupby('Category').agg({'App': pd.Series.count})
cat_merged_df = pd.merge(cat_number, category_installs, on='Category', how="inner")
print(f'The dimensions of the DataFrame are: {cat_merged_df.shape}')
cat_merged_df.sort_values('Installs', ascending=False)

scatter = px.scatter(cat_merged_df, x='App', y='Installs', title='Category Concentration', size='App', hover_name=cat_merged_df.index, color='Installs')
scatter.update_layout(xaxis_title='Number of Apps (Lower=More Concentration)', yaxis_title='Installs', yaxis=dict(type='log'))
scatter.show()

# 12. Extracting nested data from the 'Genres' column
len(df_apps_clean.Genres.unique())
df_apps_clean.Genres.value_counts().sort_values(ascending=True)[:5]
stack = df_apps_clean.Genres.str.split(';', expand=True).stack()
print(f'We now have a single column with shape: {stack.shape}')
num_genres = stack.value_counts()
print(f'Number of genres: {len(num_genres)}')

# Colour Scales in Plotly Charts - Competition in Genres
genre_bar = px.bar(x=num_genres.index[:15], y=num_genres.values[:15], title='Top Genres', hover_name=num_genres.index[:15], color=num_genres.values[:15], color_continuous_scale='Agsunset')
genre_bar.update_layout(xaxis_title='Genre', yaxis_title='Number of Apps', coloraxis_showscale=False)
genre_bar.show()

# Grouped Bar Charts: Free vs. Paid Apps per Category
df_apps_clean.Type.value_counts()
df_free_vs_paid = df_apps_clean.groupby(["Category", "Type"], as_index=False).agg({'App': pd.Series.count})
df_free_vs_paid.head()

g_bar = px.bar(df_free_vs_paid, x='Category', y='App', title='Free vs Paid Apps by Category', color='Type', barmode='group')
g_bar.update_layout(xaxis_title='Category', yaxis_title='Number of Apps', xaxis={'categoryorder': 'total descending'}, yaxis=dict(type='log'))
g_bar.show()

# Plotly Box Plots: Lost Downloads for Paid Apps
box = px.box(df_apps_clean, y='Installs', x='Type', color='Type', notched=True, points='all', title='How Many Downloads are Paid Apps Giving Up?')
box.update_layout(yaxis=dict(type='log'))
box.show()

# Plotly Box Plots: Revenue by App Category
df_paid_apps = df_apps_clean[df_apps_clean['Type'] == 'Paid']
box = px.box(df_paid_apps, x='Category', y='Revenue_Estimate', title='How Much Can Paid Apps Earn?')
box.update_layout(xaxis_title='Category', yaxis_title='Paid App Ballpark Revenue', xaxis={'categoryorder': 'min ascending'}, yaxis=dict(type='log'))
box.show()

# 13. Pricing Strategy: Paid App Prices by Category
df_paid_apps.Price.median()  # 2.99
box = px.box(df_paid_apps, x='Category', y="Price", title='Price per Category')
box.update_layout(xaxis_title='Category', yaxis_title='Paid App Price', xaxis={'categoryorder': 'max descending'}, yaxis=dict(type='log'))
box.show()
