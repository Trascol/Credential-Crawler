"""Returns a tailored resume to potentially use to apply to a specific job listing"""

# Function to generate a tailored resume based on the job listing and user profile
def generate_tailored_resume(job_field, job_skills, user_skills, user_info):
    tailored_resume = ""

    # Add basic information from the user profile (e.g., name, contact)
    tailored_resume += f"Name: {user_info['name']}\n"
    tailored_resume += f"Contact: {user_info['contact']}\n"
    tailored_resume += f"Email: {user_info['email']}\n\n"

    # Add job field
    tailored_resume += f"Objective: Seeking a position in {job_field} where I can leverage my skills in {', '.join(job_skills)}.\n\n"

    # Add Skills section, filtering based on job listing
    tailored_resume += "Skills:\n"
    for skill in user_skills:
        if skill.lower() in [s.lower() for s in job_skills]:
            tailored_resume += f"- {skill}\n"

    # Add experience section if the job listing requires specific experience
    tailored_resume += "\nExperience:\n"
    tailored_resume += user_info['experience']  # Assuming the user info has an experience section

    # Add education section (for now, just using the user profile, this can be expanded)
    tailored_resume += "\nEducation:\n"
    tailored_resume += user_info['education']  # Assuming the user info has an education section

    return tailored_resume

# Example usage
if __name__ == "__main__":
    # Example user profile
    user_info = {
        'name': 'John Doe',
        'contact': '123-456-7890',
        'email': 'john.doe@example.com',
        'experience': "Software Developer at XYZ Corp. - 3 years of experience building web applications.",
        'education': "B.S. in Computer Science, University of Tech."
    }

    # Example parsed job listing data
    job_field = "Web Development"
    job_skills = ['html', 'css', 'javascript', 'react', 'python']  # Skills required in the job listing

    # Example user skills (user's profile)
    user_skills = ['HTML', 'CSS', 'JavaScript', 'React', 'Python', 'Java']

    # Generate the tailored resume
    tailored_resume = generate_tailored_resume(job_field, job_skills, user_skills, user_info)

    # Output the tailored resume
    print("Tailored Resume:\n")
    print(tailored_resume)
