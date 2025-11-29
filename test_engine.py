from search_engine import get_search_engine

def test_engine():
    engine = get_search_engine()
    
    # Test simple instantiation
    print("Engine created.")
    
    # We won't run full search to avoid network delays/blocks in this quick check, 
    # but we can call it with empty query to see if it crashes before network.
    # Actually, let's try a quick search for CVPR or AAAI since they might be faster than OpenReview full fetch.
    
    # Test AAAI (DBLP API)
    print("Testing AAAI search...")
    results = engine.search("AAAI", "2023", "transformer")
    print(f"AAAI Results: {len(results)}")
    if results:
        print(results[0])

if __name__ == "__main__":
    test_engine()
