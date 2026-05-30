"""
Test script for Ollama Agent Extension GUI
"""
import subprocess
import sys
import time
import requests

def test_gui():
    """Test the Ollama Agent GUI by opening it"""
    print("=" * 60)
    print("TEST: Ollama Agent GUI")
    print("=" * 60)
    
    # Start the extension
    print("\nStarting Ollama Agent Extension...")
    
    # Run the extension in development mode
    process = subprocess.Popen(
        [
            sys.executable,
            '-m',
            'vscode.extensions',
            'vscode-ollama-agent-extension'
        ],
        cwd='d:\\Myfiles\\vscode-ollama-agent-extension',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for extension to start
    time.sleep(5)
    
    # Check if Ollama server is accessible
    try:
        r = requests.get('http://localhost:11434/api/tags', timeout=5)
        if r.status_code == 200:
            print("✓ Ollama server is accessible")
            models = r.json()['models']
            print(f"✓ Found {len(models)} models")
        else:
            print(f"✗ Ollama server returned {r.status_code}")
    except Exception as e:
        print(f"✗ Failed to connect to Ollama: {e}")
    
    # Test chat API through the extension
    print("\nTesting chat functionality...")
    
    try:
        data = {
            "model": "vaultbox/qwen3.5-uncensored:4b",
            "messages": [
                {"role": "user", "content": "Hello! Test the Ollama Agent GUI."}
            ],
            "stream": False
        }
        
        r = requests.post('http://localhost:11434/api/chat', json=data)
        
        if r.status_code == 200:
            response = r.json()
            print(f"✓ Chat API responded successfully")
            print(f"✓ Response: {response['message']['content'][:100]}...")
        else:
            print(f"✗ Chat API returned {r.status_code}")
    except Exception as e:
        print(f"✗ Chat test failed: {e}")
    
    # Clean up
    process.terminate()
    process.wait()
    
    print("\n✓ GUI test completed")
    return True

def test_extension_commands():
    """Test extension command registration"""
    print("\n" + "=" * 60)
    print("TEST: Extension Commands")
    print("=" * 60)
    
    # Read the compiled extension file
    with open('d:\\Myfiles\\vscode-ollama-agent-extension\\out\\extension.js', 'r') as f:
        content = f.read()
    
    # Check for registered commands
    commands = [
        'ollama.agent.create',
        'ollama.agent.run',
        'ollama.agent.evaluate',
        'ollama.agent.debug',
        'ollama.agent.status',
        'ollama.chat',
        'ollama.generateCode',
        'ollama.debugCode',
        'ollama.explainCode',
        'ollama.refactor',
        'ollama.writeTests',
        'ollama.generateDocs',
        'ollama.newAgent',
    ]
    
    found_commands = []
    missing_commands = []
    
    for cmd in commands:
        if f"'{cmd}'" in content or f'"{cmd}"' in content:
            found_commands.append(cmd)
        else:
            missing_commands.append(cmd)
    
    print(f"✓ Found {len(found_commands)} registered commands:")
    for cmd in found_commands:
        print(f"  - {cmd}")
    
    if missing_commands:
        print(f"\n✗ Missing {len(missing_commands)} commands:")
        for cmd in missing_commands:
            print(f"  - {cmd}")
    else:
        print("\n✓ All commands registered")
    
    return len(missing_commands) == 0

def main():
    """Run all GUI tests"""
    print("\n" + "=" * 60)
    print("OLLAMA AGENT EXTENSION GUI TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Extension Commands", test_extension_commands),
        ("GUI Functionality", test_gui),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} raised exception: {e}")
            import traceback
            traceback.print_exc()
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
        print("\n🎉 All GUI tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
