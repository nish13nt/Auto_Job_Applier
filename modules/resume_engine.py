import os
import json
import requests
import re
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
    
    flowables.append(Paragraph(f"<b>{data.get('name', '')}</b>", name_style))
    
    c = data.get('contact', {})
    phone = c.get('phone', '')
    email = f"<a href='mailto:{c.get('email', '')}' color='blue'>{c.get('email', '')}</a>"
    linkedin = f"<a href='{c.get('linkedin', '')}' color='blue'>LinkedIn</a>"
    github = f"<a href='{c.get('github', '')}' color='blue'>GitHub</a>"
    trailhead = f"<a href='{c.get('trailhead', '')}' color='blue'>Trailhead</a>"
    
    contact_str = f"{phone} | {email} | {linkedin} | {github} | {trailhead}"
    flowables.append(Paragraph(contact_str, contact_style))
    
    flowables.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", section_header_style))
    flowables.append(Paragraph(data.get('summary', ''), normal_style))
    
    flowables.append(Paragraph("<b>TECHNICAL SKILLS</b>", section_header_style))
    flowables.append(Paragraph(data.get('skills', ''), normal_style))
    
    if data.get('experience'):
        flowables.append(Paragraph("<b>EXPERIENCE</b>", section_header_style))
        for exp in data['experience']:
            header = f"<b>{exp.get('role', '')}</b> | {exp.get('company', '')} | {exp.get('duration', '')}"
            flowables.append(Paragraph(header, bold_item_style))
            bullets = [ListItem(Paragraph(b, normal_style)) for b in exp.get('bullets', [])]
            flowables.append(ListFlowable(bullets, bulletType='bullet', leftIndent=12))
            flowables.append(Spacer(1, 3)) 

    if data.get('projects'):
        flowables.append(Paragraph("<b>PROJECTS</b>", section_header_style))
        for proj in data['projects']:
            header = f"<b>{proj.get('name', '')}</b> | {proj.get('year', '')}"
            flowables.append(Paragraph(header, bold_item_style))
            bullets = [ListItem(Paragraph(b, normal_style)) for b in proj.get('bullets', [])]
            flowables.append(ListFlowable(bullets, bulletType='bullet', leftIndent=12))
            flowables.append(Spacer(1, 3)) 

    if data.get('education'):
        flowables.append(Paragraph("<b>EDUCATION</b>", section_header_style))
        for edu in data['education']:
            edu_str = f"<b>{edu.get('degree', '')}</b> — {edu.get('institution', '')} ({edu.get('duration', '')}) - {edu.get('score', '')}"
            flowables.append(Paragraph(edu_str, normal_style))
            flowables.append(Spacer(1, 2))
            
    if data.get('certifications') or data.get('leadership'):
        flowables.append(Paragraph("<b>CERTIFICATIONS & LEADERSHIP</b>", section_header_style))
        for cert in data.get('certifications', []):
            flowables.append(Paragraph(f"• {cert.get('title', '')} ({cert.get('date', '')})", normal_style))
        for lead in data.get('leadership', []):
            flowables.append(Paragraph(f"• {lead.get('title', '')}, {lead.get('organization', '')} ({lead.get('duration', '')})", normal_style))

    doc.build(flowables)
    print(f"📄 Generated 1-Page ATS PDF: {output_path}")
    return output_path

def get_available_models(api_key):
    """Bypass dynamic discovery to prevent API rate limiting."""
    print("📋 Bypassing dynamic discovery. Forcing gemini-3.1-flash-lite...")
    return ["gemini-3.1-flash-lite"]

async def create_tailored_resume(job_title, job_requirements, company_name):
    print(f"🧠 Tailoring full resume for: {job_title} at {company_name}...")
    
    with open("data/master_profile.json", "r") as f:
        master_profile = f.read()
        
    prompt = f"""
    You are an elite ATS resume optimizer. I am applying for the role of "{job_title}".
    
    Here are the Job Requirements: 
    {job_requirements}
    
    Here is my Master Profile JSON:
    {master_profile}
    
    CRITICAL INSTRUCTIONS FOR CUSTOMIZATION:
    1. KEYWORD EXTRACTION: First, silently analyze the Job Requirements and extract the core technical skills.
    2. AGGRESSIVE REWRITING: Rewrite my "summary" and experience/project "bullets" to heavily emphasize the specific keywords found in the JD. 
    3. SKILL REORDERING: Reorder the "skills" list so the exact technologies requested in the JD appear first.
    4. NO DELETIONS: DO NOT DELETE any work experience, projects, or education. Keep all factual history, but change the focal point to match the JD.
    5. OUTPUT FORMAT: Output ONLY a raw, valid JSON object matching the schema below. No markdown.
    
    SCHEMA:
    {{
        "name": "string",
        "contact": {{"email": "string", "phone": "string", "linkedin": "string", "github": "string", "trailhead": "string"}},
        "summary": "string",
        "skills": "string",
        "education": [{{"institution": "string", "degree": "string", "duration": "string", "score": "string"}}],
        "experience": [{{"company": "string", "role": "string", "duration": "string", "bullets": ["string"]}}],
        "projects": [{{"name": "string", "year": "string", "bullets": ["string"]}}],
        "leadership": [{{"title": "string", "organization": "string", "duration": "string"}}],
        "certifications": [{{"title": "string", "date": "string"}}]
    }}
    """
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return None

    models_to_try = get_available_models(api_key)
    
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json", "temperature": 0.0}
        }
        
        try:
            response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
            if response.status_code == 200:
                result_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                clean_text = result_text.replace('```json', '').replace('```', '').strip()
                
                try:
                    tailored_data = json.loads(clean_text)
                except json.JSONDecodeError as json_err:
                    print(f"⚠️ {model} returned invalid JSON: {json_err}")
                    continue
                
                # Sanitize the company name for Windows file paths
                clean_company = re.sub(r'[\\/*?:"<>|]', "", company_name)
                clean_company = clean_company.replace(' ', '_').strip()
                pdf_path = f"temp/Nishant-Survase-{clean_company}.pdf"
                
                return generate_pdf(tailored_data, pdf_path)
            else:
                print(f"⚠️ {model} API Error ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"⚠️ Python/Network Error with {model}: {e}")
            continue
            
    print("\n❌ Failed to generate resume.")
    return None