from supabase import create_client, Client
import os
import random
from datetime import datetime
from typing import List
from dotenv import load_dotenv

load_dotenv()

def add_attendance_batch(prefix: str, eventid: str, member_ids: List[str]) -> dict:
    supabase: Client = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    
    def generate_unique_certificate():
        while True:
            current_year = datetime.now().year
            year_suffix = str(current_year)[-2:]
            random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(7)])
            certificate = f"{prefix}{year_suffix}-{random_numbers}"
            
            # Check if certificate exists
            existing = supabase.table("attendance").select("certificate").eq("certificate", certificate).execute()
            if not existing.data:
                return certificate
    
    try:
        print(f"Looking up {len(member_ids)} members...")
        members_response = supabase.table("members").select("id").in_("memberid", member_ids).execute()
        
        if not members_response.data:
            print("No members found!")
            return {"success": False, "error": "No members found"}
        
        member_db_ids = [member["id"] for member in members_response.data]
        print(f"Found {len(member_db_ids)} members")
        
        attendance_records = []
        for member_id in member_db_ids:
            certificate = generate_unique_certificate()
            attendance_records.append({
                "memberid": member_id,
                "eventid": eventid,
                "certificate": certificate
            })
        
        print(f"Creating {len(attendance_records)} attendance records...")
        result = supabase.table("attendance").insert(attendance_records).execute()
        print("✓ Attendance records added successfully!")
        
        return {
            "success": True,
            "data": result.data,
            "records_added": len(attendance_records)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("Starting batch attendance script...")
    
    result = add_attendance_batch(
        prefix="ygg",
        eventid="6f4e4193-2b2d-4dd1-bb36-c804f61886f0",
        member_ids=["aws26-0637"]
    )
    
    if result["success"]:
        print(f"Success! Added {result['records_added']} records")
    else:
        print(f"Error: {result['error']}")