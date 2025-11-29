import sys
print(sys.executable)
print(sys.path)
import openreview

def test_search():
    print("Initializing OpenReview client...")
    client = openreview.Client(baseurl='https://api.openreview.net')
    
    # Try to search for ICLR 2024 papers
    # Common venue ID for ICLR 2024
    venue_id = 'ICLR.cc/2024/Conference'
    
    print(f"Searching for papers in {venue_id}...")
    
    # Getting accepted papers usually involves a specific invitation or verifying the content.venueid
    # Let's try to get a few notes from ICLR 2024 to see the structure
    try:
        notes = client.get_notes(content={'venueid': venue_id}, limit=5)
        if not notes:
            print("No notes found with simple venueid search. Trying 'ICLR.cc/2024/Conference/-/Submission'")
            notes = client.get_notes(invitation='ICLR.cc/2024/Conference/-/Submission', limit=5)
        
        print(f"Found {len(notes)} notes.")
        for note in notes:
            print(f"Title: {note.content.get('title')}")
            print(f"Keywords: {note.content.get('keywords')}")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
