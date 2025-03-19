# This will be used to parse through job listings,

# then when the user wants to apply, we parse through the job listing, gather what field this is in, what skills we would need
# then from this take the users resume/skills and create a brand new resume based around what the job listing would want
# ex/ jr. Web dev

# blah blah blah HTML, CSS, Javascript

# take skills and field and match it to user,
# If user skills match job listing skills then add to users resume
# once done doing a bunch of stuff apply to the job listing

import re

# Function to parse the job listing and extract useful information
def parse_job_listing(job_listing):
    job_field = ""
    skills_required = []
    experience_required = ""
    job_description = ""

    # Example keywords to identify the job field
    job_field_keywords = ['web development', 'software engineer', 'data analyst', 'developer', 'designer', 'jr.', 'senior']
    for field in job_field_keywords:
        if field.lower() in job_listing.lower():
            job_field = field
            break
    
    # Example skill extraction (could be expanded based on job listing)
    skills_keywords = ['html', 'css', 'javascript', 'python', 'java', 'react', 'sql', 'nodejs', 'aws', 'ruby']
    for skill in skills_keywords:
        if skill.lower() in job_listing.lower():
            skills_required.append(skill)

    # Extracting experience level or requirements (e.g. "3+ years of experience")
    experience_pattern = r"(\d+\+? years? of experience)"
    experience_match = re.search(experience_pattern, job_listing, re.IGNORECASE)
    if experience_match:
        experience_required = experience_match.group(1)

    # Extracting job description (up to the point of experience or skills section)
    job_description = job_listing.split('Required skills:')[0] if 'Required skills:' in job_listing else job_listing

    return job_field, skills_required, experience_required, job_description

# Example usage
if __name__ == "__main__":
    # Example job listing text
    job_listing = """
    We are looking for a Junior Web Developer to join our team. 
    Required skills: HTML, CSS, JavaScript, React, and a good understanding of front-end development.
    Experience with Python or Node.js is a plus. 2+ years of experience preferred.
    Responsibilities include building and maintaining web applications, debugging, and collaborating with other team members.
    """

    # Parse the job listing to extract the useful information
    job_field, skills_required, experience_required, job_description = parse_job_listing(job_listing)

    # Output the parsed information
    print(f"Job Field: {job_field}")
    print(f"Required Skills: {', '.join(skills_required)}")
    print(f"Experience Required: {experience_required}")
    print(f"Job Description:\n{job_description}")
