import os
import re
import json
import requests
import asyncio
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Force load environment to override old cached keys
load_dotenv(override=True)

# Import custom engines
from modules.resume_engine import create_tailored_resume
from modules.browser_agent import run_application_agent

# The waiting room for pending OTPs/Captchas
user_futures = {} 

async def extract_job_details(job_url):
    """Scrapes the job page and uses Gemini to extract Title, Company, and Requirements."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found.")
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(job_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.extract()
        page_text = " ".join(soup.stripped_strings)[:10000]
        
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={api_key}"
        
        prompt = f"""
        Analyze this webpage text and extract the Job Title, Company Name, and core Job Requirements.
        Text: {page_text}
        
        Output ONLY a raw, valid JSON object with this exact structure:
        {{
            "title": "Exact Job Title",
            "company": "Exact Company Name",
            "requirements": "Comma separated list of main technical requirements and skills"
        }}
        """
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        
        res = requests.post(gemini_url, headers={'Content-Type': 'application/json'}, json=payload)
        data = res.json()
        
        if 'candidates' not in data:
            print(f"⚠️ API Error during extraction: {data}")
            return {"title": "Software Engineer", "company": "Company", "requirements": "Software Development, Python, Salesforce, Java"}

        result_text = data['candidates'][0]['content']['parts'][0]['text']
        clean_text = result_text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    
    except Exception as e:
        print(f"⚠️ Failed to extract job details: {e}")
        return {"title": "Software Engineer", "company": "Company", "requirements": "Software Development, Python, Salesforce, Java"}


async def process_job_application(update: Update, context: ContextTypes.DEFAULT_TYPE, job_url: str, chat_id: int):
    """The background task that runs the heavy lifting invisibly."""
    try:
        job_details = await extract_job_details(job_url)
        job_title = job_details.get("title", "Software Engineer")
        job_company = job_details.get("company", "Company")
        job_requirements = job_details.get("requirements", "")
        
        await context.bot.send_message(chat_id=chat_id, text=f"🎯 Target Acquired: {job_title} at {job_company}\n\n🧠 Generating highly tailored 1-page ATS Resume...")
        
        pdf_path = await create_tailored_resume(job_title, job_requirements, job_company)
        
        if not pdf_path:
            await context.bot.send_message(chat_id=chat_id, text="❌ Failed to generate the resume due to API limits. Application aborted.")
            return
            
        await context.bot.send_message(chat_id=chat_id, text="📄 Resume generated successfully! \n\n🚀 Deploying Browser Agent. I will ping you if I hit an OTP or Captcha wall...")
        absolute_pdf_path = os.path.abspath(pdf_path)
        
        async def request_otp_from_tg(reason: str) -> str:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"⚠️ **HUMAN INTERVENTION NEEDED** ⚠️\n\n**AI Says:** {reason}\n\n👉 **Please reply to this message within 90 seconds with the OTP/Code.**"
            )
            loop = asyncio.get_running_loop()
            future = loop.create_future()
            user_futures[chat_id] = future
            
            try:
                otp_code = await future 
                return otp_code
            except asyncio.CancelledError:
                return "Error: Timeout"
            finally:
                if chat_id in user_futures:
                    del user_futures[chat_id]
        
        agent_result = await run_application_agent(job_url, absolute_pdf_path, request_otp_from_tg)
        
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Application Pipeline Complete!\n\nAgent Report:\n{agent_result}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ An error occurred during the pipeline: {str(e)}")
        if chat_id in user_futures:
            del user_futures[chat_id]


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Listens for links and OTP replies."""
    message_text = update.message.text
    chat_id = update.message.chat_id
    
    if chat_id in user_futures and not user_futures[chat_id].done():
        await update.message.reply_text("🤖 Got it! Feeding this to the AI Agent right now...")
        user_futures[chat_id].set_result(message_text)
        return

    url_match = re.search(r'(https?://[^\s]+)', message_text)
    
    if not url_match:
        await update.message.reply_text("🤖 Please send me a valid job link (URL) to apply!")
        return

    job_url = url_match.group(0)
    await update.message.reply_text(f"🔍 Link received! Initializing background process for:\n{job_url}")
    
    asyncio.create_task(process_job_application(update, context, job_url, chat_id))


def main():
    """Starts the Telegram Bot."""
    print("🤖 Auto-Job Applier Bot is waking up...")
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN is missing from your .env file!")
        return

    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is online and listening for job links! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()