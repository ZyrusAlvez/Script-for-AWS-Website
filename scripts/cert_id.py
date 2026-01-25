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
        members_response = supabase.table("members").select("id, firstname, lastname").in_("memberid", member_ids).execute()
        
        if not members_response.data:
            return {"success": False, "error": "No members found"}
        
        attendance_records = []
        for member in members_response.data:
            certificate = generate_unique_certificate()
            attendance_records.append({
                "memberid": member["id"],
                "eventid": eventid,
                "certificate": certificate
            })
            full_name = f"{member['firstname']} {member['lastname']}"
            print(f"{full_name} - {certificate}")
        
        result = supabase.table("attendance").insert(attendance_records).execute()
        print(f"✓ Saved {len(attendance_records)} records to attendance table")
        
        return {
            "success": True,    
            "data": result.data,
            "records_added": len(attendance_records)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = add_attendance_batch(
        prefix="da",
        eventid="6f4e4193-2b2d-4dd1-bb36-c804f61886f0",
        member_ids=["aws26-0637"]
    )
    
    if not result["success"]:
        print(f"Error: {result['error']}")