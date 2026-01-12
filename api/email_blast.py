from http.server import BaseHTTPRequestHandler
import json
import smtplib
from email.message import EmailMessage
import os
from supabase import create_client, Client

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read the webhook payload
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract member data from Supabase webhook
            # Supabase sends: {"type": "INSERT", "table": "members", "record": {...}, "old_record": null}
            record = data.get('record', {})
            
            firstname = record.get('firstname')
            memberid = record.get('memberid')
            schoolemail = record.get('schoolemail')
            
            # Validate required fields
            if not all([firstname, memberid, schoolemail]):
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "Missing required fields",
                    "received": record
                }).encode())
                return
            
            # Send the email
            send_welcome_email(firstname, memberid, schoolemail)
            
            # Update email_sent to true
            supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
            supabase.table("members").update({"email_sent": True}).eq("memberid", memberid).execute()
            
            # Success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "message": f"Email sent to {schoolemail}"
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e)
            }).encode())
    
    def do_GET(self):
        # Health check endpoint
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "message": "AWS Learning Club Email Webhook is running"
        }).encode())


def send_welcome_email(name, membership_id, email):
    """Send welcome email to new member"""
    EMAIL = os.environ.get("EMAIL")
    PASSWORD = os.environ.get("PASSWORD")
    
    msg = EmailMessage()
    msg["From"] = EMAIL
    msg["To"] = email
    msg["Subject"] = "🎉 Welcome to AWS Learning Club - UPHSL!"
    msg.set_content(
        f"Hi {name}, congratulations! Your membership has been approved. "
        f"Your Membership ID is: {membership_id}"
    )
    msg.add_alternative(template(name, membership_id), subtype='html')
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)


def template(name, membership_id):
    return f"""
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      @media only screen and (max-width: 600px) {{
        .main-title {{ font-size: 24px !important; }}
        .subtitle {{ font-size: 13px !important; }}
        .welcome-heading {{ font-size: 18px !important; }}
        .body-text {{ font-size: 14px !important; }}
        .membership-id {{ font-size: 20px !important; letter-spacing: 1px !important; }}
        .id-card {{ padding: 16px !important; min-width: 0 !important; }}
        .section-padding {{ padding: 20px !important; }}
        .id-section-padding {{ padding: 20px !important; }}
        .id-header {{ padding: 12px 20px !important; }}
        .next-steps {{ font-size: 16px !important; }}
        .list-text {{ font-size: 13px !important; }}
      }}
    </style>
  </head>
  <body style="margin:0; padding:0; font-family: 'Arial', sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);">
    <div style="max-width:672px; margin:auto; padding:20px;">
      
      <!-- Banner Image -->
      <div style="width:100%; border-radius:8px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.3);">
        <img src="https://aws-learning-club-uphsl.vercel.app/awslc banner.jpg" alt="AWS Learning Club Banner" style="width:100%; display:block;"/>
      </div>

      <!-- Main Content Card -->
      <div style="margin-top:32px; background:rgba(255,255,255,0.1); backdrop-filter:blur(10px); border-radius:0; border:1px solid rgba(255,255,255,0.2); box-shadow:0 8px 32px rgba(0,0,0,0.2); overflow:hidden;">
        
        <!-- Orange Header Bar -->
        <div style="background:#ffa23f; padding:0; height:8px;"></div>

        <!-- Welcome Section -->
        <div class="section-padding" style="padding:32px; text-align:center;">
          <h1 class="main-title" style="margin:0; font-size:36px; font-weight:800; color:#fff;">
            <span style="color:#ffa23f; font-weight:900;">AWS</span> Learning Club
          </h1>
          <h2 class="subtitle" style="margin:8px 0 0; font-size:16px; font-weight:700; color:#fff;">
            University of Perpetual Help System Laguna - Biñan
          </h2>
          
          <div style="border-bottom:1px solid rgba(255,255,255,0.2); margin:24px 0;"></div>
          
          <div style="text-align:left;">
            <h2 class="welcome-heading" style="margin:0 0 16px; font-size:20px; font-weight:700; color:#ffa23f;">
              🎉 Welcome to the Club!
            </h2>
            <p class="body-text" style="margin:0 0 16px; font-size:16px; line-height:1.6; color:rgba(255,255,255,0.8);">
              Hi <strong style="color:#fff;">{name}</strong>,
            </p>
            <p class="body-text" style="margin:0 0 16px; font-size:16px; line-height:1.6; color:rgba(255,255,255,0.8);">
              Congratulations! 🎊 Your membership application has been <strong style="color:#ffa23f;">approved</strong>! We're thrilled to officially welcome you to the Amazon Web Services (AWS) Learning Club — a space where we grow our cloud knowledge and collaborate with fellow learners and enthusiasts!
            </p>
            <p class="body-text" style="margin:0 0 16px; font-size:16px; line-height:1.6; color:rgba(255,255,255,0.8);">
              You're now part of a community dedicated to exploring the future of cloud computing. Let's build, learn, and innovate together! ☁️🚀
            </p>
          </div>
        </div>

        <!-- Membership ID Section -->
        <div class="id-header" style="background:#ffa23f; padding:16px 32px;">
          <p style="margin:0; font-size:14px; font-weight:700; color:rgba(255,255,255,0.8); text-align:center;">
            YOUR MEMBERSHIP ID
          </p>
        </div>
        
        <div class="id-section-padding" style="padding:32px; text-align:center; background:rgba(0,0,0,0.1);">
          <div class="id-card" style="background:rgba(255,255,255,0.15); border:2px solid rgba(255,255,255,0.3); border-radius:8px; padding:20px; margin:0 auto; max-width:100%;">
            <p style="margin:0 0 8px; font-size:12px; color:rgba(255,255,255,0.7); font-weight:600;">
              Membership ID
            </p>
            <h2 class="membership-id" style="margin:0; font-size:24px; font-weight:900; color:#ffa23f; letter-spacing:1.5px; font-family:'Courier New', monospace; word-break:break-all;">
              {membership_id}
            </h2>
          </div>
          
          <p class="body-text" style="margin:20px 0 0; font-size:13px; line-height:1.6; color:rgba(255,255,255,0.7);">
            Use this ID to verify your membership, track your progress, and showcase your contributions to the community.
          </p>
        </div>

        <!-- Next Steps Section -->
        <div class="section-padding" style="padding:32px; border-top:1px solid rgba(255,255,255,0.2);">
          <h3 class="next-steps" style="margin:0 0 16px; font-size:18px; font-weight:700; color:#ffa23f;">
            What's Next?
          </h3>
          <ul class="list-text" style="margin:0; padding-left:20px; color:rgba(255,255,255,0.8); font-size:15px; line-height:1.8;">
            <li style="margin-bottom:8px;">Join our community channels and stay updated on events</li>
            <li style="margin-bottom:8px;">Attend our upcoming workshops and training sessions</li>
            <li style="margin-bottom:8px;">Connect with fellow members and start collaborating</li>
            <li style="margin-bottom:8px;">Explore AWS resources and begin your cloud journey</li>
          </ul>
          
          <p class="body-text" style="margin:24px 0 0; font-size:16px; color:#fff; font-weight:600; text-align:right;">
            See you in the club! 🌟
          </p>
          <p class="body-text" style="margin:4px 0 0; font-size:16px; color:#fff; font-weight:600; text-align:right;">
            – Awie
          </p>
        </div>

        <!-- Footer -->
        <div class="section-padding" style="padding:20px 32px; text-align:center; font-size:13px; color:rgba(255,255,255,0.6); background:rgba(0,0,0,0.2); border-top:1px solid rgba(255,255,255,0.1);">
          Questions? Contact us at <a href="mailto:awslc.uphsl@gmail.com" style="color:#ffa23f; text-decoration:none; font-weight:600;">awslc.uphsl@gmail.com</a>
        </div>
      </div>

      <!-- Bottom spacing -->
      <div style="height:20px;"></div>
    </div>
  </body>
</html>
"""