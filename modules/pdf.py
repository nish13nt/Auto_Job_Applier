import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

os.makedirs("temp", exist_ok=True)

def generate_pdf(data, output_path):
    """Draws a fully structured, ATS-compliant 1-PAGE PDF."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    name_style = ParagraphStyle('Name', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=14, spaceAfter=2)
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, spaceAfter=6)
    section_header_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=11, spaceAfter=2, spaceBefore=6)
    bold_item_style = ParagraphStyle('BoldItem', parent=styles['Normal'], fontSize=9.5, fontName='Helvetica-Bold', spaceAfter=1)
    normal_style = ParagraphStyle('Standard', parent=styles['Normal'], fontSize=9.5, spaceAfter=1, leading=11)
    
    flowables = []
    
    # 1. Header
    flowables.append(Paragraph(f"<b>{data.get('name', '')}</b>", name_style))
    
    c = data.get('contact', {})
    contact_str = f"{c.get('phone', '')} | <a href='mailto:{c.get('email', '')}' color='blue'>{c.get('email', '')}</a> | <a href='{c.get('linkedin', '')}' color='blue'>LinkedIn</a> | <a href='{c.get('github', '')}' color='blue'>GitHub</a> | {c.get('availability', '')}"
    flowables.append(Paragraph(contact_str, contact_style))
    
    # 2. Professional Summary
    flowables.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", section_header_style))
    flowables.append(Paragraph(data.get('summary', ''), normal_style))
    
    # 3. Technical Skills
    flowables.append(Paragraph("<b>TECHNICAL SKILLS</b>", section_header_style))
    flowables.append(Paragraph(data.get('skills', ''), normal_style))
    
    # 4. Professional Experience
    if data.get('experience'):
        flowables.append(Paragraph("<b>EXPERIENCE</b>", section_header_style))
        for exp in data['experience']:
            header = f"<b>{exp.get('role', '')}</b> | {exp.get('company', '')} | {exp.get('duration', '')}"
            flowables.append(Paragraph(header, bold_item_style))
            bullets = [ListItem(Paragraph(b, normal_style)) for b in exp.get('bullets', [])]
            flowables.append(ListFlowable(bullets, bulletType='bullet', leftIndent=12))
            flowables.append(Spacer(1, 3))

    # 5. Projects
    if data.get('projects'):
        flowables.append(Paragraph("<b>PROJECTS</b>", section_header_style))
        for proj in data['projects']:
            header = f"<b>{proj.get('name', '')}</b> | {proj.get('year', '')}"
            flowables.append(Paragraph(header, bold_item_style))
            bullets = [ListItem(Paragraph(b, normal_style)) for b in proj.get('bullets', [])]
            flowables.append(ListFlowable(bullets, bulletType='bullet', leftIndent=12))
            flowables.append(Spacer(1, 3))

    # 6. Education
    if data.get('education'):
        flowables.append(Paragraph("<b>EDUCATION</b>", section_header_style))
        for edu in data['education']:
            edu_str = f"<b>{edu.get('degree', '')}</b> — {edu.get('institution', '')} ({edu.get('duration', '')}) - {edu.get('score', '')}"
            flowables.append(Paragraph(edu_str, normal_style))
            flowables.append(Spacer(1, 2))
            
    # 7. Certifications & Leadership
    if data.get('certifications') or data.get('leadership'):
        flowables.append(Paragraph("<b>CERTIFICATIONS & LEADERSHIP</b>", section_header_style))
        for cert in data.get('certifications', []):
            flowables.append(Paragraph(f"• {cert.get('title', '')} ({cert.get('date', '')})", normal_style))
        for lead in data.get('leadership', []):
            flowables.append(Paragraph(f"• {lead.get('title', '')}, {lead.get('organization', '')} ({lead.get('duration', '')})", normal_style))

    doc.build(flowables)
    print(f"📄 Generated 1-Page ATS PDF: {output_path}")
    return output_path

if __name__ == "__main__":
    # Hardcoded resume data (No API calls)
    resume_data = {
        "name": "Nishant Babasaheb Survase",
        "contact": {
            "phone": "+91 93568 93551",
            "email": "nishantsurvase98@gmail.com",
            "linkedin": "linkedin.com/in/nishantsurvase",
            "github": "github.com/nishantsurvase",
            "availability": "Immediate Joiner"
        },
        "summary": "Highly analytical Computer Science graduate with a 9.02 CGPA, skilled in Python, SQL, and Salesforce. Proven experience in building automated data pipelines and processing large datasets to drive operational efficiency. Immediate joiner ready to leverage modern data engineering tools.",
        "skills": "Languages & Databases: Python, MySQL, C++ | AI Tools: Gemini, Claude, n8n, Zapier | Backend & Frameworks: REST APIs, Git, GitHub | Other: Salesforce (Apex, SOQL, Agentforce)",
        "experience": [
            {
                "company": "Tata Consultancy Services",
                "role": "Salesforce Developer Intern",
                "duration": "Jan 2026 - Jul 2026",
                "bullets": [
                    "Engineered scalable Python automation scripts to streamline data processing workflows, successfully handling dynamic file date extraction and advanced data mapping.",
                    "Developed custom logic to resolve complex SSO mismatches and prioritize data fields across multiple queries, minimizing logging overhead by generating concise, match-count success reports.",
                    "Utilized SOQL and backend logic to extract, transform, and load (ETL) large-scale data feeds, improving operational efficiency and ensuring seamless integration across cloud platforms."
                ]
            },
            {
                "company": "Glow Genesis Skincare Pvt. Ltd.",
                "role": "Software Development Intern",
                "duration": "Sept 2024 - Feb 2025",
                "bullets": [
                    "Developed and enhanced application features, improving user experience, application responsiveness, and overall system performance.",
                    "Integrated APIs, resolved application data issues, and collaborated with the development team to deliver stable and scalable solutions."
                ]
            }
        ],
        "projects": [
            {
                "name": "Autonomous Job Application Data Pipeline",
                "year": "2026",
                "bullets": [
                    "Built an end-to-end autonomous browser agent to continuously monitor external sources, parse unstructured job links, and automate complex application workflows in the background.",
                    "Engineered an AI-driven data processing engine to dynamically extract job requirements and cross-reference them with a master profile, automatically generating ATS-optimized PDF resumes.",
                    "Designed a scalable, headless execution environment featuring a Human-in-the-Loop system via Telegram to seamlessly manage security challenges (CAPTCHA/OTP)."
                ]
            },
            {
                "name": "Railway Station Navigation System",
                "year": "2026",
                "bullets": [
                    "Developed, designed, and implemented a highly scalable AR indoor navigation solution using Flutter, Unity, and A* routing to guide users across multi-point indoor paths with step-wise directions.",
                    "Implemented and optimized FastAPI APIs for route generation and navigation updates, reducing response latency and enabling near real-time user guidance."
                ]
            },
            {
                "name": "Customer Churn Prediction Platform",
                "year": "2025",
                "bullets": [
                    "Developed a machine learning-based customer churn prediction platform using Python, SQL, Pandas, and Scikit-Learn to analyze 7,000+ customer records and identify customers at risk of churn.",
                    "Performed data preprocessing and predictive modeling, utilizing dashboard visualizations to track key metrics and user data, driving operational excellence and generating actionable retention insights."
                ]
            }
        ],
        "education": [
            {
                "institution": "JSPM's Rajarshi Shahu College of Engineering, Pune",
                "degree": "B.Tech Computer Science & Business Systems",
                "duration": "Nov 2022 - June 2026",
                "score": "CGPA: 9.02"
            }
        ],
        "certifications": [
            {"title": "Salesforce Certified Agentforce Specialist", "date": "Dec 2025"}
        ],
        "leadership": [
            {"title": "Co-Organizer", "organization": "TEDxJSPMRSCOE", "duration": "2024-2025"},
            {"title": "Training and Placement Co-ordinator", "organization": "RSCOE", "duration": "2024-2025"}
        ]
    }
    
    output_filename = "temp/Nishant-Survase-DataEngineering.pdf"
    generate_pdf(resume_data, output_filename)