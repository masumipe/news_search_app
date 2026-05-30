"""
Test script for Ollama Agent Extension
"""
import requests
import json

def test_ollama_server():
    """Test Ollama server connection"""
    print("=" * 50)
    print("TEST 1: Ollama Server Connection")
    print("=" * 50)
    
    # Test health check
    try:
        r = requests.get('http://localhost:11434/api/tags')
        if r.status_code == 200:
            models = r.json()['models']
            print(f"✓ Ollama server is running")
            print(f"✓ Available models: {len(models)}")
            for model in models[:3]:
                print(f"  - {model['name']}")
        else:
            print(f"✗ Ollama server returned status {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to connect to Ollama: {e}")
        return False
    
    return True

def test_chat_api():
    """Test Ollama chat API"""
    print("\n" + "=" * 50)
    print("TEST 2: Chat API")
    print("=" * 50)
    
    try:
        data = {
            "model": "vaultbox/qwen3.5-uncensored:4b",
            "messages": [
                {"role": "user", "content": "What is the capital of France?"}
            ],
            "stream": False
        }
        
        r = requests.post('http://localhost:11434/api/chat', json=data)
        
        if r.status_code == 200:
            response = r.json()
            print(f"✓ Chat API responded with status {r.status_code}")
            print(f"✓ Response length: {len(response['message']['content'])} characters")
            print(f"✓ Response preview: {response['message']['content'][:100]}...")
        else:
            print(f"✗ Chat API returned status {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Chat API failed: {e}")
        return False
    
    return True

def test_generate_api():
    """Test Ollama generate API"""
    print("\n" + "=" * 50)
    print("TEST 3: Generate API")
    print("=" * 50)
    
    try:
        data = {
            "model": "vaultbox/qwen3.5-uncensored:4b",
            "prompt": "Write a Python function to calculate factorial",
            "stream": False
        }
        
        r = requests.post('http://localhost:11434/api/generate', json=data)
        
        if r.status_code == 200:
            response = r.json()
            print(f"✓ Generate API responded with status {r.status_code}")
            print(f"✓ Response length: {len(response['response'])} characters")
            print(f"✓ Response preview: {response['response'][:100]}...")
        else:
            print(f"✗ Generate API returned status {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Generate API failed: {e}")
        return False
    
    return True

def test_agent_commands():
    """Test agent creation and management"""
    print("\n" + "=" * 50)
    print("TEST 4: Agent Commands")
    print("=" * 50)
    
    try:
        # Test create agent
        agent_name = "Test Agent"
        data = {
            "name": agent_name,
            "description": "A test agent for testing purposes",
            "model": "vaultbox/qwen3.5-uncensored:4b",
            "system_prompt": "You are a helpful assistant."
        }
        
        r = requests.post('http://localhost:11434/api/chat', json=data)
        
        if r.status_code == 200:
            print(f"✓ Agent creation API responded with status {r.status_code}")
            print(f"✓ Response preview: {r.json()['message']['content'][:100]}...")
        else:
            print(f"✗ Agent creation API returned status {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Agent creation failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("OLLAMA AGENT EXTENSION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Ollama Server Connection", test_ollama_server),
        ("Chat API", test_chat_api),
        ("Generate API", test_generate_api),
        ("Agent Commands", test_agent_commands),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} raised exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
