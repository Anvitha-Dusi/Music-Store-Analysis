# Music Store Data Analysis - Visualizations
# Python script to run SQL queries and plot charts
# Course Project / Assignment

import sqlite3
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set a nice clean style for plots
sns.set_theme(style="whitegrid")
plt.rcParams['font.size'] = 10

# Get directory of this script on the system so paths always work
script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.join(script_dir, "dataset")
output_folder = os.path.join(script_dir, "output")

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

print("Loading dataset into SQLite in-memory database...")

# Step 1: Connect to in-memory SQLite database and load CSVs
conn = sqlite3.connect(":memory:")

# Loop through all CSV files in dataset folder using relative system path
csv_files = glob.glob(os.path.join(dataset_dir, "*.csv"))
for file_path in csv_files:
    table_name = os.path.splitext(os.path.basename(file_path))[0]
    df = pd.read_csv(file_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)

print(f"Loaded {len(csv_files)} tables from '{dataset_dir}' successfully!\n")


# -------------------------------------------------------------------
# Visualization 1: Q2 - Which countries have the most invoices?
# -------------------------------------------------------------------
print("Generating Plot 1: Top 10 Countries by Invoices...")
query_1 = """
SELECT billing_country AS country, COUNT(invoice_id) AS total_invoices
FROM invoice
GROUP BY billing_country
ORDER BY total_invoices DESC
LIMIT 10;
"""
df_q1 = pd.read_sql_query(query_1, conn)

plt.figure(figsize=(9, 5))
bars = plt.bar(df_q1['country'], df_q1['total_invoices'], color='steelblue', edgecolor='black')
plt.title("Top 10 Countries by Total Invoices (Q2)", fontsize=13, fontweight='bold')
plt.xlabel("Country", fontsize=11)
plt.ylabel("Number of Invoices", fontsize=11)
plt.xticks(rotation=30, ha='right')

# Add values on top of bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, int(yval), ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(f"{output_folder}/q2_top_countries_invoices.png", dpi=300)
plt.close()


# -------------------------------------------------------------------
# Visualization 2: Q4 - Which city has the highest revenue (best customers)?
# -------------------------------------------------------------------
print("Generating Plot 2: Top 10 Cities by Revenue...")
query_2 = """
SELECT billing_city AS city, ROUND(SUM(total), 2) AS total_revenue
FROM invoice
GROUP BY billing_city
ORDER BY total_revenue DESC
LIMIT 10;
"""
df_q2 = pd.read_sql_query(query_2, conn)

plt.figure(figsize=(9, 5))
# Highlight the top city in coral and others in skyblue
colors = ['coral' if i == 0 else 'skyblue' for i in range(len(df_q2))]
bars = plt.bar(df_q2['city'], df_q2['total_revenue'], color=colors, edgecolor='black')
plt.title("Top 10 Cities by Total Revenue (Q4)", fontsize=13, fontweight='bold')
plt.xlabel("City", fontsize=11)
plt.ylabel("Total Revenue ($)", fontsize=11)
plt.xticks(rotation=35, ha='right')

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 3, f"${yval:.1f}", ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig(f"{output_folder}/q4_top_cities_revenue.png", dpi=300)
plt.close()


# -------------------------------------------------------------------
# Visualization 3: Q7 - Top 10 Rock Artists / Bands with Most Songs
# -------------------------------------------------------------------
print("Generating Plot 3: Top 10 Rock Bands...")
query_3 = """
SELECT artist.name AS artist_name, COUNT(track.track_id) AS num_of_songs
FROM artist
JOIN album ON album.artist_id = artist.artist_id
JOIN track ON track.album_id = album.album_id
WHERE genre_id IN (
    SELECT genre_id 
    FROM genre 
    WHERE name LIKE 'Rock'
)
GROUP BY artist.artist_id
ORDER BY num_of_songs DESC
LIMIT 10;
"""
df_q3 = pd.read_sql_query(query_3, conn)

plt.figure(figsize=(9, 5))
# Horizontal bar chart for artist names
plt.barh(df_q3['artist_name'][::-1], df_q3['num_of_songs'][::-1], color='mediumpurple', edgecolor='black')
plt.title("Top 10 Rock Artists by Track Count (Q7)", fontsize=13, fontweight='bold')
plt.xlabel("Number of Songs", fontsize=11)
plt.ylabel("Artist / Band", fontsize=11)

# Add text labels on each bar
for index, value in enumerate(df_q3['num_of_songs'][::-1]):
    plt.text(value + 1, index, str(value), va='center', fontsize=9)

plt.tight_layout()
plt.savefig(f"{output_folder}/q7_top_rock_artists.png", dpi=300)
plt.close()


# -------------------------------------------------------------------
# Visualization 4: Q8 - Track Length Distribution vs Average Track Length
# -------------------------------------------------------------------
print("Generating Plot 4: Song Length Distribution...")
query_4 = """
SELECT milliseconds / 60000.0 AS duration_minutes
FROM track;
"""
df_q4 = pd.read_sql_query(query_4, conn)
avg_len = df_q4['duration_minutes'].mean()

plt.figure(figsize=(9, 5))
# Filter out extreme outliers (> 15 mins like audiobooks/podcasts) for cleaner student graph
df_filtered = df_q4[df_q4['duration_minutes'] <= 15]

plt.hist(df_filtered['duration_minutes'], bins=30, color='teal', edgecolor='black', alpha=0.7)
plt.axvline(avg_len, color='red', linestyle='--', linewidth=2, label=f"Average Length: {avg_len:.2f} mins")

plt.title("Distribution of Song Durations (Q8)", fontsize=13, fontweight='bold')
plt.xlabel("Duration (Minutes)", fontsize=11)
plt.ylabel("Number of Tracks", fontsize=11)
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig(f"{output_folder}/q8_song_duration_distribution.png", dpi=300)
plt.close()


# -------------------------------------------------------------------
# Visualization 5: Q10 / Q14 - Most Popular Music Genres by Purchases
# -------------------------------------------------------------------
print("Generating Plot 5: Music Genre Share...")
query_5 = """
SELECT genre.name AS genre_name, COUNT(invoice_line.quantity) AS total_purchases
FROM invoice_line
JOIN track ON track.track_id = invoice_line.track_id
JOIN genre ON genre.genre_id = track.genre_id
GROUP BY genre.name
ORDER BY total_purchases DESC;
"""
df_q5 = pd.read_sql_query(query_5, conn)

# Group smaller genres into 'Others' so pie chart looks clean
top_n = 5
top_genres = df_q5.iloc[:top_n].copy()
others_sum = df_q5.iloc[top_n:]['total_purchases'].sum()
top_genres.loc[len(top_genres)] = {'genre_name': 'Others', 'total_purchases': others_sum}

plt.figure(figsize=(7, 7))
palette = sns.color_palette("pastel")[0:len(top_genres)]
plt.pie(
    top_genres['total_purchases'], 
    labels=top_genres['genre_name'], 
    autopct='%1.1f%%', 
    startangle=140, 
    colors=palette,
    wedgeprops={'edgecolor': 'black', 'linewidth': 0.8}
)
plt.title("Most Popular Music Genres by Purchases (Q10/Q14)", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{output_folder}/q10_popular_genres_pie.png", dpi=300)
plt.close()


# -------------------------------------------------------------------
# Visualization 6: Q12 - Top 10 Most Popular Artists by Track Purchases
# -------------------------------------------------------------------
print("Generating Plot 6: Top 10 Popular Artists...")
query_6 = """
SELECT artist.name AS artist_name, COUNT(invoice_line.quantity) AS purchases
FROM invoice_line
JOIN track ON track.track_id = invoice_line.track_id
JOIN album ON album.album_id = track.album_id
JOIN artist ON artist.artist_id = album.artist_id
GROUP BY artist.artist_id
ORDER BY purchases DESC
LIMIT 10;
"""
df_q6 = pd.read_sql_query(query_6, conn)

plt.figure(figsize=(9, 5))
bars = plt.bar(df_q6['artist_name'], df_q6['purchases'], color='salmon', edgecolor='black')
plt.title("Top 10 Most Popular Artists by Purchases (Q12)", fontsize=13, fontweight='bold')
plt.xlabel("Artist", fontsize=11)
plt.ylabel("Number of Track Purchases", fontsize=11)
plt.xticks(rotation=35, ha='right')

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, int(yval), ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(f"{output_folder}/q12_popular_artists.png", dpi=300)
plt.close()

# Close database connection
conn.close()

print("\nAll visualizations created and saved successfully in the 'output/' directory! :)")
