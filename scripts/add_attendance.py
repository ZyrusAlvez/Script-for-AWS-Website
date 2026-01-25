from supabase import create_client, Client
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

def add_attendance(member_ids: List[str], event_ids: List[str]) -> dict:
    """
    Add attendance records for given member IDs and event IDs.
    
    Args:
        member_ids: List of member identifiers to look up in members table
        event_ids: List of event IDs for attendance records
    
    Returns:
        dict: Result with success status and data/error info
    """
    # Initialize Supabase client
    supabase: Client = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    
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
            for event_id in event_ids:
                attendance_records.append({
                    "memberid": member_id,
                    "eventid": event_id
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
    print("Starting attendance script...")
    
    result = add_attendance(
        member_ids=["aws26-0495", "aws26-0342"], 
        event_ids=["ae777e91-9def-44ee-b86f-05e8048ee0ff"
]
    )
    
    if result["success"]:
        print(f"Success! Added {result['records_added']} records")
    else:
        print(f"Error: {result['error']}")
