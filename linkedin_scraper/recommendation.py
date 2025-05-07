import pandas as pd

# Load the cleaned job data
df = pd.read_csv('raw_jobs.csv')

# Explode skill lists and clean
df['skills'] = df['skills'].str.strip("[]").str.replace("'", "").str.split(", ")
df = df.explode('skills')
df['skills'] = df['skills'].str.lower().str.strip()

def recommend_cities_for_skill(skill):
    if not isinstance(skill, str) or not skill.strip():
        print("Invalid input: Skill must be a non-empty string.")
        return
    skill = skill.lower().strip()
    result = df[df['skills'] == skill]
    if result.empty:
        print(f"No demand found for skill: {skill}")
        return
    demand_by_city = result['location'].value_counts()
    print(f"\n🧠 Job demand for skill: '{skill}':\n")
    print(demand_by_city)

# Example usage
skill_input = input("Enter a skill (e.g., python, sql, aws): ")
recommend_cities_for_skill(skill_input)
