"""Builds a resume and/or job listing based off of users input as sections that build on each other"""

#NOTE: NEED TO UPDATE, BUT I WANT TO BUILD THE RESUME USING LATEX. NEED TO GET ALL THE INFO FROM THE USER ON A FRONT END DIALOGUE WINDOW STUFF

import os

# Function to collect personal info
def get_personal_info():
    print("Enter your personal info:")
    name = input("Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    return {
        "name": name,
        "email": email,
        "phone": phone
    }

# Function to collect skills
def get_skills():
    print("\nEnter your skills (comma-separated): ")
    skills = input().split(',')
    skills = [skill.strip() for skill in skills]  # Clean extra spaces
    return skills

# Function to collect experience
def get_experience():
    experience = []
    print("\nEnter your job experience:")
    while True:
        job_title = input("Job Title (or 'done' to finish): ")
        if job_title.lower() == 'done':
            break
        company = input("Company: ")
        start_date = input("Start Date: ")
        end_date = input("End Date: ")
        responsibilities = input("Responsibilities (comma-separated): ").split(',')
        responsibilities = [resp.strip() for resp in responsibilities]  # Clean extra spaces
        experience.append({
            "job_title": job_title,
            "company": company,
            "start_date": start_date,
            "end_date": end_date,
            "responsibilities": responsibilities
        })
    return experience

# Function to collect education info
def get_education():
    education = []
    print("\nEnter your education details:")
    while True:
        degree = input("Degree (or 'done' to finish): ")
        if degree.lower() == 'done':
            break
        institution = input("Institution: ")
        graduation_year = input("Graduation Year: ")
        education.append({
            "degree": degree,
            "institution": institution,
            "graduation_year": graduation_year
        })
        
        add_another = input("Do you want to add another education entry? (yes/no): ").strip().lower()
        if add_another != 'yes':
            break
    return education

# Function to generate LaTeX resume
def generate_latex_resume(data):
    latex_resume = r"\documentclass[a4paper,10pt]{article}"
    latex_resume += r"\usepackage{geometry}"
    latex_resume += r"\geometry{top=1in, bottom=1in, left=1in, right=1in}"
    latex_resume += r"\usepackage{enumitem}"
    latex_resume += r"\begin{document}"

    # Personal Info
    latex_resume += r"\begin{center}"
    latex_resume += r"\textbf{\Huge " + data['personal_info']['name'] + r"}\\"
    latex_resume += r"\texttt{" + data['personal_info']['email'] + r"}\\"
    latex_resume += r"\texttt{" + data['personal_info']['phone'] + r"}"
    latex_resume += r"\end{center}"

    latex_resume += r"\section*{Skills}"
    latex_resume += r"\begin{itemize}[label=-]"
    for skill in data['skills']:
        latex_resume += f"\item {skill}"
    latex_resume += r"\end{itemize}"

    # Experience
    latex_resume += r"\section*{Experience}"
    for exp in data['experience']:
        latex_resume += r"\textbf{" + exp['job_title'] + r"} \hfill " + exp['start_date'] + r" - " + exp['end_date'] + r"\\"
        latex_resume += r"\textit{" + exp['company'] + r"}\\"
        latex_resume += r"\begin{itemize}[label=-]"
        for resp in exp['responsibilities']:
            latex_resume += f"\item {resp}"
        latex_resume += r"\end{itemize}"

    # Education
    latex_resume += r"\section*{Education}"
    for edu in data['education']:
        latex_resume += r"\textbf{" + edu['degree'] + r"} \hfill " + edu['graduation_year'] + r"\\"
        latex_resume += r"\textit{" + edu['institution'] + r"}\\"

    latex_resume += r"\end{document}"

    return latex_resume

# Function to save the LaTeX resume to a file
def save_latex_resume(latex_text):
    filename = input("\nEnter filename to save the resume (e.g., 'resume.tex'): ")
    with open(filename, 'w') as file:
        file.write(latex_text)
    print(f"Resume saved to {filename}")

# Main function to build the resume
def build_resume():
    resume_data = {}

    print("Welcome to the LaTeX Resume Builder!")

    # Collect personal information
    resume_data['personal_info'] = get_personal_info()

    # Collect skills
    resume_data['skills'] = get_skills()

    # Collect experience
    resume_data['experience'] = get_experience()

    # Collect education (with dynamic sections)
    resume_data['education'] = get_education()

    # Generate LaTeX formatted resume
    latex_text = generate_latex_resume(resume_data)

    print("\nHere is your LaTeX-formatted resume:\n")
    print(latex_text)

    # Save LaTeX resume
    save_latex_resume(latex_text)

# Run the script
if __name__ == "__main__":
    build_resume()
