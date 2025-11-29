import sys
print(sys.executable)
import openreview

def test_search_v2():
    print("Initializing OpenReview API v2 client...")
    # API v2 client
    client = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')
    
    venue_id = 'ICLR.cc/2023/Conference'
    print(f"Searching for papers in {venue_id} using API v2...")
    
    try:
        # API v2 usually uses 'venue_id' in get_notes or similar, but the signature might differ
        # checking submissions
        submissions = client.get_notes(content={'venueid': venue_id}, limit=5)
        
        print(f"Found {len(submissions)} notes via venueid.")
        for note in submissions:
            print(f"Title: {note.content.get('title', {}).get('value')}") # v2 content is often a dict with 'value'
            print("-" * 20)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search_v2()
