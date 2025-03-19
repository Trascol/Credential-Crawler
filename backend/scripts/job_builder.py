"""Builds a job listing based off of users input as sections that build on each other"""



# Function to collect job title and company
def get_job_title_and_company():
    print("Enter job details:")
    job_title = input("Job Title: ")
    company = input("Company: ")
    return job_title, company

# Function to collect job description
def get_job_description():
    print("\nEnter job description:")
    description = input("Description: ")
    return description

# Function to collect job requirements
def get_job_requirements():
    requirements = []
    print("\nEnter job requirements:")
    while True:
        requirement = input("Requirement (or 'done' to finish): ")
        if requirement.lower() == 'done':
            break
        requirements.append(requirement)
    return requirements

# Function to collect skills required for the job
def get_job_skills():
    print("\nEnter skills required for the job (comma-separated): ")
    skills = input().split(',')
    skills = [skill.strip() for skill in skills]  # Clean extra spaces
    return skills

# Function to collect compensation information
def get_compensation():
    print("\nEnter compensation details:")
    salary = input("Salary Range (e.g., 50,000 - 60,000): ")
    benefits = input("Benefits: ")
    return salary, benefits

# Function to generate the job listing
def generate_job_listing(data):
    job_listing = f"Job Title: {data['job_title']} at {data['company']}\n"
    job_listing += f"Description:\n{data['description']}\n\n"
    
    job_listing += "Requirements:\n"
    for req in data['requirements']:
        job_listing += f"- {req}\n"
    
    job_listing += "\nSkills Required:\n"
    for skill in data['skills']:
        job_listing += f"- {skill}\n"
    
    job_listing += "\nCompensation:\n"
    job_listing += f"Salary Range: {data['salary']}\n"
    job_listing += f"Benefits: {data['benefits']}\n"
    
    return job_listing

# Function to save the job listing to a file
def save_job_listing(job_listing_text):
    filename = input("\nEnter filename to save the job listing (e.g., 'job_listing.txt'): ")
    with open(filename, 'w') as file:
        file.write(job_listing_text)
    print(f"Job listing saved to {filename}")

# Main function to build the job listing
def build_job_listing():
    job_listing_data = {}

    print("Welcome to the Job Listing Builder!")

    # Collect job title and company
    job_listing_data['job_title'], job_listing_data['company'] = get_job_title_and_company()

    # Collect job description
    job_listing_data['description'] = get_job_description()

    # Collect job requirements
    job_listing_data['requirements'] = get_job_requirements()

    # Collect job skills
    job_listing_data['skills'] = get_job_skills()

    # Collect compensation details
    job_listing_data['salary'], job_listing_data['benefits'] = get_compensation()

    # Generate job listing
    job_listing_text = generate_job_listing(job_listing_data)

    print("\nHere is your job listing:\n")
    print(job_listing_text)

    # Save job listing
    save_job_listing(job_listing_text)

# Run the script
if __name__ == "__main__":
    build_job_listing()
