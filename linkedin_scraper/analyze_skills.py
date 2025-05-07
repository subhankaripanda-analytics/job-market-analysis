import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os

# Set up output directory
os.makedirs('outputs', exist_ok=True)

# Step 1: Load the dataset
# - Reads 'raw_jobs.csv' with columns: title, location, skills (skills is empty: [])
df = pd.read_csv('raw_jobs.csv')

# Step 2: Assign skills to job titles since skills column is empty
# - Maps job title keywords to relevant skills
skill_keywords = {
    'mobile app developer': ['swift', 'kotlin', 'react native'],
    'software engineer': ['python', 'java', 'sql'],
    'full stack': ['javascript', 'react', 'node.js', 'sql'],
    'web developer': ['html', 'css', 'javascript'],
    'react': ['react', 'javascript', 'node.js'],
    'administrative': ['communication', 'organization'],
    'iot': ['iot', 'python', 'c++'],
    'javascript': ['javascript', 'react', 'node.js'],
    'ruby': ['ruby', 'rails', 'javascript'],
    'php': ['php', 'laravel', 'mysql'],
    'spokesperson': ['public speaking', 'communication'],  # Matches 'spoke person'
    'data engineer': ['python', 'sql', 'spark'],
    'angular': ['angular', 'javascript', 'typescript']
}

def assign_skills(title):
    # Convert title to lowercase for matching
    title = title.lower()
    # Check each keyword in skill_keywords
    for keyword, skills in skill_keywords.items():
        if keyword in title:
            return list(set(skills))  # Return unique skills
    return ['general']  # Default for unmatched titles

# Apply skill assignment and explode skills list into separate rows
df['skills'] = df['title'].apply(assign_skills)
df = df.explode('skills')
df['skills'] = df['skills'].str.lower().str.strip()
df.dropna(subset=['skills'], inplace=True)

# Step 3: Streamlit web interface
st.title("Job Market Analysis Tool")
st.write("Explore job skills and recommendations based on job postings.")

# Sidebar for navigation
st.sidebar.header("Select an Action")
action = st.sidebar.selectbox("Choose an option:", [
    "View Heatmap",
    "View Top Skills Bar Plot",
    "View Skill Pie Chart for Job Title",
    "Recommend Job Titles for a Skill",
    "Recommend Complementary Skills"
])

# Action 1: Heatmap of top skills by job title
if action == "View Heatmap":
    st.header("Heatmap: Top Skills by Job Title")
    # Group data by title and skill, count occurrences
    top_skills = df.groupby(['title', 'skills']).size().reset_index(name='count')
    # Select top 5 skills per title, exclude grouping columns to fix deprecation warning
    top_skills = top_skills.groupby('title').apply(
        lambda x: x.nlargest(5, 'count')[['skills', 'count']],
        include_groups=False
    ).reset_index()
    # Shorten job titles for readability
    top_skills['title_short'] = top_skills['title'].apply(lambda x: x[:20] + '...' if len(x) > 20 else x)
    # Create pivot table for heatmap
    heatmap_data = top_skills.pivot_table(index='skills', columns='title_short', values='count', fill_value=0)
    # Plot heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, cmap='YlGnBu', fmt='.0f')
    plt.title("Top Skills by Job Title")
    plt.tight_layout()
    plt.savefig('outputs/heatmap.png')
    st.pyplot(plt)

# Action 2: Bar plot of top 10 skills
elif action == "View Top Skills Bar Plot":
    st.header("Bar Plot: Top 10 Most In-Demand Skills")
    # Count the most common skills
    top_skills_overall = df['skills'].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_skills_overall.values, y=top_skills_overall.index, palette='Blues_d')
    plt.title('Top 10 Most In-Demand Skills')
    plt.xlabel('Number of Postings')
    plt.ylabel('Skills')
    plt.tight_layout()
    plt.savefig('outputs/top_skills_bar.png')
    st.pyplot(plt)

# Action 3: Pie chart for a specific job title
elif action == "View Skill Pie Chart for Job Title":
    st.header("Pie Chart: Skill Distribution for a Job Title")
    job_title = st.text_input("Enter a job title (e.g., Software Engineer, Full Stack):")
    if st.button("Show Pie Chart"):
        if not job_title.strip():
            st.error("Please enter a valid job title.")
        else:
            job_title = job_title.lower().strip()
            job_data = df[df['title'].str.contains(job_title, case=False, na=False)]['skills'].value_counts()
            if job_data.empty:
                st.error(f"No skills found for job title: {job_title}")
            else:
                plt.figure(figsize=(8, 8))
                plt.pie(job_data, labels=job_data.index, autopct='%1.1f%%', startangle=90)
                plt.title(f'Skill Distribution for {job_title}')
                plt.tight_layout()
                plt.savefig(f'outputs/skills_pie_{job_title.replace(" ", "_")}.png')
                st.pyplot(plt)

# Action 4: Recommend job titles for a skill
elif action == "Recommend Job Titles for a Skill":
    st.header("Recommend Job Titles for a Skill")
    skill = st.text_input("Enter a skill (e.g., python, sql):")
    if st.button("Get Recommendations"):
        if not skill.strip():
            st.error("Invalid input: Skill must be a non-empty string.")
        else:
            skill = skill.lower().strip()
            result = df[df['skills'] == skill]
            if result.empty:
                st.error(f"No demand found for skill: {skill}")
            else:
                demand_by_job = result['title'].value_counts()
                st.write(f"**Job titles requiring skill: '{skill}'**")
                st.write(demand_by_job)
                # Export to CSV
                csv_file = f'outputs/recommendations_{skill}.csv'
                demand_by_job.to_csv(csv_file)
                st.write(f"Recommendations saved to {csv_file}")
                # Provide download button
                with open(csv_file, 'rb') as f:
                    st.download_button(
                        label="Download Recommendations",
                        data=f,
                        file_name=csv_file,
                        mime='text/csv'
                    )

# Action 5: Recommend complementary skills
elif action == "Recommend Complementary Skills":
    st.header("Recommend Complementary Skills")
    skill = st.text_input("Enter a skill (e.g., python, sql):")
    if st.button("Get Complementary Skills"):
        if not skill.strip():
            st.error("Invalid input: Skill must be a non-empty string.")
        else:
            skill = skill.lower().strip()
            job_skills = df.groupby(df.index)['skills'].apply(list)
            relevant_jobs = df[df['skills'] == skill].index
            co_skills = job_skills[job_skills.index.isin(relevant_jobs)].explode().value_counts()
            co_skills = co_skills[co_skills.index != skill].head(5)
            if co_skills.empty:
                st.error(f"No complementary skills found for: {skill}")
            else:
                st.write(f"**Skills commonly paired with '{skill}'**")
                st.write(co_skills)

# Footer
st.sidebar.write("Built with Streamlit")