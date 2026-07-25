import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from Backend.services.ai import match_knowledge_base

def run_tests():
    print("Starting keyword matching logic tests...\n")
    
    # Test Case 1: cow + "মুখে ফোসকা লালা ঝরছে" -> should match FMD entry
    print("Test Case 1: cow + 'মুখে ফোসকা লালা ঝরছে'")
    results1 = match_knowledge_base("মুখে ফোসকা লালা ঝরছে", "cow")
    print(f"Matched {len(results1)} entries:")
    for r in results1:
        print(f"  - Animal: {r.get('animal')}, Disease: {r.get('disease')}, Symptoms: {r.get('key_symptoms')}")
    assert any(r.get('animal') == 'cow' and ('FMD' in r.get('disease') or 'খুরা রোগ' in r.get('disease')) for r in results1), "Test Case 1 Failed: FMD not matched"
    print("Test Case 1 Passed!\n")

    # Test Case 2: duck + "হঠাৎ মৃত্যু পাতলা সবুজ পায়খানা" -> should match Duck Viral Enteritis entry
    print("Test Case 2: duck + 'হঠাৎ মৃত্যু পাতলা সবুজ পায়খানা'")
    results2 = match_knowledge_base("হঠাৎ মৃত্যু পাতলা সবুজ পায়খানা", "duck")
    print(f"Matched {len(results2)} entries:")
    for r in results2:
        print(f"  - Animal: {r.get('animal')}, Disease: {r.get('disease')}, Symptoms: {r.get('key_symptoms')}")
    assert any(r.get('animal') == 'duck' and ('Duck Viral Enteritis' in r.get('disease') or 'ডাক প্লেগ' in r.get('disease')) for r in results2), "Test Case 2 Failed: Duck Viral Enteritis not matched"
    print("Test Case 2 Passed!\n")

    # Test Case 3: vague/unrelated input -> should match zero entries
    print("Test Case 3: 'আমার মাথা ব্যথা করছে' (vague/unrelated input)")
    results3 = match_knowledge_base("আমার মাথা ব্যথা করছে", None)
    print(f"Matched {len(results3)} entries.")
    assert len(results3) == 0, f"Test Case 3 Failed: Matched {len(results3)} entries instead of 0"
    print("Test Case 3 Passed!\n")

    # Test Case 4: No animal type specified but animal mentioned in text: "আমার গরুর মুখে ফোসকা আর লালা ঝরছে"
    print("Test Case 4: No animal type specified, 'আমার গরুর মুখে ফোসকা আর লালা ঝরছে'")
    results4 = match_knowledge_base("আমার গরুর মুখে ফোসকা আর লালা ঝরছে", None)
    print(f"Matched {len(results4)} entries:")
    for r in results4:
        print(f"  - Animal: {r.get('animal')}, Disease: {r.get('disease')}, Symptoms: {r.get('key_symptoms')}")
    assert any(r.get('animal') == 'cow' and 'খুরা রোগ' in r.get('disease') for r in results4), "Test Case 4 Failed: Cow FMD not matched"
    # Ensure no other animal diseases are matched
    assert all(r.get('animal') == 'cow' for r in results4), "Test Case 4 Failed: Matched non-cow diseases"
    print("Test Case 4 Passed!\n")

    print("All test cases passed successfully!")

if __name__ == "__main__":
    run_tests()
