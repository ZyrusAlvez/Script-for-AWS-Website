import os
import smtplib
from email.message import EmailMessage
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
# Set IS_TEST_MODE to True to send ONLY to your own email for verification.
# Set to False when you are ready to send to everyone.
IS_TEST_MODE = True 
MY_TEST_EMAIL = "c23-1275-381@uphsl.edu.ph" # Your email for testing

# Initialize Supabase
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def send_certificate_email(firstname, email, cert_id, cert_data):
    """Send certificate email with PNG attachment"""
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")
    
    msg = EmailMessage()
    msg["From"] = EMAIL
    msg["To"] = email
    msg["Subject"] = "Thank You for Attending – Your Certificate & Resources Inside!"
    msg.set_content(f"Hi {firstname}, your certificate is attached to this email.")
    msg.add_alternative(certificate_template(firstname), subtype='html')
    msg.add_attachment(cert_data, maintype='image', subtype='png', filename=f'{cert_id}.png')
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

def certificate_template(name):
    return f"""
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      @media only screen and (max-width: 600px) {{
        .main-title {{ font-size: 24px !important; }}
        .body-text {{ font-size: 14px !important; }}
      }}
    </style>
  </head>
  <body style="margin:0; padding:0; font-family: 'Arial', sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);">
    <div style="max-width:672px; margin:auto; padding:20px;">
      
      <div style="width:100%; border-radius:8px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.3);">
        <img src="https://aws-learning-club-uphsl.vercel.app/awslc banner.jpg" alt="AWS Learning Club Banner" style="width:100%; display:block;"/>
      </div>

      <div style="margin-top:32px; background:rgba(255,255,255,0.1); backdrop-filter:blur(10px); border-radius:0; border:1px solid rgba(255,255,255,0.2); box-shadow:0 8px 32px rgba(0,0,0,0.2); overflow:hidden;">
        
        <div style="background:#ffa23f; padding:0; height:8px;"></div>

        <div style="padding:32px; text-align:center;">
          <h1 class="main-title" style="margin:0; font-size:36px; font-weight:800; color:#fff;">
            <span style="color:#ffa23f; font-weight:900;">AWS</span> Learning Club
          </h1>
          <h2 style="margin:8px 0 0; font-size:16px; font-weight:700; color:#fff;">
            University of Perpetual Help System Laguna - Biñan
          </h2>
          
          <div style="border-bottom:1px solid rgba(255,255,255,0.2); margin:24px 0;"></div>
          
          <div style="text-align:left;">
            <h2 style="margin:0 0 16px; font-size:20px; font-weight:700; color:#ffa23f;">
              🎉 Congratulations on Completing the Workshop!
            </h2>
            <p class="body-text" style="margin:0 0 16px; font-size:16px; line-height:1.6; color:rgba(255,255,255,0.8);">
              Hi <strong style="color:#fff;">{name}</strong>,
            </p>
            <p class="body-text" style="margin:0 0 16px; font-size:16px; line-height:1.6; color:rgba(255,255,255,0.8);">
              Thank you for attending our workshop! 🎊 We're excited to share your <strong style="color:#ffa23f;">Certificate of Completion</strong> with you. Your dedication to learning and growing your cloud skills is truly inspiring!
            </p>
            <p class="body-text" style="margin:0 0 16px; font-size:16px; line-height:1.6; color:rgba(255,255,255,0.8);">
              Your certificate is attached to this email. Feel free to share it on LinkedIn, add it to your portfolio, or showcase it however you'd like! 🏆
            </p>
          </div>
        </div>

        <div style="padding:32px; border-top:1px solid rgba(255,255,255,0.2);">
          <h3 style="margin:0 0 16px; font-size:18px; font-weight:700; color:#ffa23f;">
            Keep Learning!
          </h3>
          <ul style="margin:0; padding-left:20px; color:rgba(255,255,255,0.8); font-size:15px; line-height:1.8;">
            <li style="margin-bottom:8px;">Join our upcoming workshops and events</li>
            <li style="margin-bottom:8px;">Connect with fellow learners in our community</li>
            <li style="margin-bottom:8px;">Continue exploring AWS and cloud technologies</li>
            <li style="margin-bottom:8px;">Share your learning journey with others</li>
          </ul>
          
          <p style="margin:24px 0 0; font-size:16px; color:#fff; font-weight:600; text-align:right;">
            Keep building! 🌟
          </p>
          <p style="margin:4px 0 0; font-size:16px; color:#fff; font-weight:600; text-align:right;">
            – AWS Learning Club Team
          </p>
        </div>

        <div style="padding:20px 32px; text-align:center; font-size:13px; color:rgba(255,255,255,0.6); background:rgba(0,0,0,0.2); border-top:1px solid rgba(255,255,255,0.1);">
          Questions? Contact us at <a href="mailto:awslc.uphsl@gmail.com" style="color:#ffa23f; text-decoration:none; font-weight:600;">awslc.uphsl@gmail.com</a>
        </div>
      </div>

      <div style="height:20px;"></div>
    </div>
  </body>
</html>
"""

def main():
    """Main function to send certificate emails"""
    # 1. GUEST LIST: Manual entries for people without website accounts
    guest_list = [
        {"firstname": "Allyza Shamel", "email": "c25-1030-748@uphsl.edu.ph", "filename": "allyza-hernandez-cert"},
        {"firstname": "Vladimir", "email": "c25-2634-143@uphsl.edu.ph", "filename": "vladimir-reyes-cert"},
        {"firstname": "Angela", "email": "c22-0927-423@uphsl.edu.ph", "filename": "angela-cabanes-cert"},
        {"firstname": "Mara Colleen", "email": "c25-2440-766@uphsl.edu.ph", "filename": "mara-espanola-cert"}
    ]

    if IS_TEST_MODE:
        print(f"\n[TEST MODE] Sending ONLY to {MY_TEST_EMAIL}\n")
        # Find the person matching MY_TEST_EMAIL in database
        try:
            response = supabase.table("attendance").select(
                "certificate, members(firstname, schoolemail)"
            ).neq("certificate", "No certificate issued").execute()
            
            # Filter for MY_TEST_EMAIL
            matching = [r for r in response.data if r["members"]["schoolemail"] == MY_TEST_EMAIL]
            
            if matching:
                record = matching[0]
                cert_id = record["certificate"]
                fname = record["members"]["firstname"]
                file_path = f"Data Analytics Workshop/{cert_id}.png"
                cert_bytes = supabase.storage.from_("certificates").download(file_path)
                send_certificate_email(fname, MY_TEST_EMAIL, cert_id, cert_bytes)
                print(f"✓ TEST: Sent certificate to {fname} ({MY_TEST_EMAIL})")
            else:
                print(f"✗ No certificate found for {MY_TEST_EMAIL} in database")
        except Exception as e:
            print(f"✗ TEST failed: {e}")
        
        print("\nTest complete. Set IS_TEST_MODE = False to send to everyone.")
        return

    # PRODUCTION MODE: Send to everyone
    print(f"\n[PRODUCTION] Sending to all recipients...\n")
    
    # Send to guests
    print(f"Sending {len(guest_list)} guest certificates...")
    for guest in guest_list:
        try:
            file_path = f"Data Analytics Workshop/{guest['filename']}.png"
            cert_bytes = supabase.storage.from_("certificates").download(file_path)
            send_certificate_email(guest["firstname"], guest["email"], guest["filename"], cert_bytes)
            print(f"✓ Sent guest cert to {guest['firstname']} ({guest['email']})")
        except Exception as e:
            print(f"✗ Failed guest {guest['firstname']}: {e}")

    print("\n" + "="*50)
    print("Now sending to database members...")
    print("="*50 + "\n")

    # Send to database members
    try:
        response = supabase.table("attendance").select(
            "certificate, members(firstname, schoolemail)"
        ).neq("certificate", "No certificate issued").execute()
        
        print(f"Found {len(response.data)} database members with certificates.\n")
        
        for record in response.data:
            cert_id = record["certificate"]
            fname = record["members"]["firstname"]
            email = record["members"]["schoolemail"]
            
            try:
                file_path = f"Data Analytics Workshop/{cert_id}.png"
                cert_bytes = supabase.storage.from_("certificates").download(file_path)
                send_certificate_email(fname, email, cert_id, cert_bytes)
                print(f"✓ Sent to {fname} ({email})")
            except Exception as e:
                print(f"✗ Failed {fname}: {e}")
                
        print("\nEmail blast completed!")
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    main()
