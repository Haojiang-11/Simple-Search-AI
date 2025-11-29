from search_engine import get_search_engine

def test_engine():
    engine = get_search_engine()
    print("Engine created.")
    
    # Test CVPR
    print("\nTesting CVPR search...")
    try:
        results = engine.search("CVPR", "2023", "diffusion")
        print(f"CVPR Results: {len(results)}")
        if results:
            print(f"First result: {results[0]['title']}")
    except Exception as e:
        print(f"CVPR Test Failed: {e}")

    # Test AAAI (DBLP API)
    print("\nTesting AAAI search...")
    try:
        results = engine.search("AAAI", "2023", "transformer")
        print(f"AAAI Results: {len(results)}")
        if results:
            print(f"First result: {results[0]['title']}")
    except Exception as e:
        print(f"AAAI Test Failed: {e}")

if __name__ == "__main__":
    test_engine()
