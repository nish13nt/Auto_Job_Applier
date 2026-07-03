import os
import asyncio
from browser_use import Agent, Browser, BrowserProfile, Controller
from browser_use import ChatGoogle

os.environ["ANONYMIZED_TELEMETRY"] = "false"

if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

async def run_application_agent(job_url, pdf_path, otp_callback=None):
    absolute_pdf_path = os.path.abspath(pdf_path)
    # 1. FIX THE PATH FOR BOTH THE PROMPT AND THE WHITELIST
    safe_pdf_path = absolute_pdf_path.replace("\\", "/")
    
    print(f"\n🚀 Booting up AI Agent to apply to: {job_url}")
    
    llm = ChatGoogle(
        model="gemini-3.1-flash-lite", 
        temperature=0.0
    )
    
    settings = BrowserProfile(
        headless=False,
        disable_security=True,
        extra_chromium_args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-popup-blocking",
            "--no-sandbox"
        ]
    )
    
    browser = Browser(browser_profile=settings)
    controller = Controller()
    
    @controller.action("request_human_help_for_otp")
    async def request_human_help_for_otp(reason: str) -> str:
        """CRITICAL: You MUST execute this tool to pause the browser and ask the user for an OTP, Captcha, or Code. Do NOT use the 'done' tool to ask for a code."""
        if otp_callback:
            print(f"⏸️ AI paused. Asking Telegram user for OTP: {reason}")
            try:
                return await asyncio.wait_for(otp_callback(reason), timeout=90.0)
            except asyncio.TimeoutError:
                return "Error: Timeout. The human did not respond."
        return "Error: No human available."
        
    task_prompt = f"""
    You are an autonomous AI Job Application Assistant.
    
    CRITICAL RULE 1 (NO HALLUCINATIONS): NEVER invent or guess information. Do not blindly type into random inputs.
    CRITICAL RULE 2 (OTP/CAPTCHA): If the website asks for a Verification Code, OTP, or Captcha, DO NOT click 'done'. You MUST execute the `request_human_help_for_otp` tool.
    CRITICAL RULE 3 (RESUME UPLOAD): You MUST upload the resume using the `upload_file` action. The absolute file path is exactly: "{safe_pdf_path}"
    CRITICAL RULE 4 (OPTIONAL MAPPING): Every form is different. If a specific field from the Applicant Profile below (like Address, Education, etc.) is NOT requested on the screen, IGNORE IT. Do not scroll endlessly looking for fields that do not exist.
    CRITICAL RULE 5 (DYNAMIC FORMS): If you need to add Education or Experience, you may need to click buttons like "Add Education" or "Add Experience" first to reveal the text boxes.
    
    1. Navigate to: {job_url}
    2. Click Apply. Prefer "Apply Manually" over "Autofill with Resume".
    
    3. Fill out the application using EXACTLY this Applicant Profile (skip what isn't asked):
       - Account Creation: If forced to create an account, use Email: nishantsurvase98@gmail.com and Password: Nishant@2026!
       - First Name: Nishant
       - Last Name: Survase
       - Full Name: Nishant Babasaheb Survase
       - Email: nishantsurvase98@gmail.com
       - Phone: +91 93568 93551
       - Address Line 1: A1, Krishna Kunj Row House, Hari Om Nagar, Artillery Centre Road
       - City: Nashik Road, Nashik
       - State/Province/Region: Maharashtra
       - Postal/Zip Code: 422102
       - Country: India
       
       [EDUCATION LOGIC]
       - Primary Degree: B.Tech Computer Science and Business Systems
       - College: JSPM's Rajarshi Shahu College of Engineering
       - College Start Date: Nov 2022
       - College End/Graduation Date: June 2026
       - CGPA: 9.02
       - 12th Grade/HSC: ONLY fill this in if the form explicitly requires secondary education. If required, use: Army Public School, Devlali, Science Stream, Passed in 2022, Score: 83.4%.
       - 10th Grade/SSC: ONLY fill this in if the form explicitly requires primary education. If required, use: Army Public School, Devlali, Science Stream, Passed in 2020, Score: 89.8%.

       [WORK/EXPERIENCE LOGIC]
       - Experience Level: Fresher / Entry Level
       - Expected CTC: [YOUR EXPECTED CTC]
       - Current Company: None / Student
       - Notice Period: 0 Days / Immediately Available
       - Work Experience: Salesforce Developer Intern
       
       [DEMOGRAPHICS]
       - Gender: Male
       - Race/Ethnicity: Asian (or Prefer not to answer)
       - Veteran Status: I am not a veteran
       - Disability Status: I do not have a disability
       - LinkedIn URL: https://www.linkedin.com/in/nishant-survase-771884251/
       - GitHub URL: https://github.com/nish13nt
       
    4. Upload the resume located at "{safe_pdf_path}".
    5. Check any required boxes for terms of service, privacy agreements, or consent.
    6. Click Submit.
    7. Return a short text summary confirming if the application was successfully submitted.
    """
    
    agent = Agent(
        task=task_prompt,
        llm=llm,
        browser=browser,
        controller=controller,
        # 2. FIX: Use the forward-slash path in the whitelist!
        available_file_paths=[safe_pdf_path]
    )
    
    result = await agent.run()
    await browser.close()
    
    final_output = result.final_result()
    print("\n✅ AI Agent Finished. Here is what it found:\n")
    print(final_output)
    
    return final_output