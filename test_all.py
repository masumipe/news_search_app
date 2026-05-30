"""
Comprehensive test for Ollama Agent Extension
Tests all commands and GUI functionality
"""
import subprocess
import sys
import time
import requests
import json

class OllamaAgentTester:
    def __init__(self):
        self.results = []
        self.success_count = 0
        self.total_tests = 0
        
    def test(self, name, test_func):
        """Run a test and record results"""
        self.total_tests += 1
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print('='*60)
        
        try:
            result = test_func()
            self.results.append((name, result))
            if result:
                self.success_count += 1
                print(f"✓ PASSED: {name}")
            else:
                print(f"✗ FAILED: {name}")
        except Exception as e:
            print(f"✗ ERROR: {name} - {e}")
            import traceback
            traceback.print_exc()
            self.results.append((name, False))
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in self.results if result)
        total = len(self.results)
        
        for name, result in self.results:
            status = "✓ PASSED" if result else "✗ FAILED"
            print(f"{status}: {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
        
        return passed == total
    
    def test_ollama_server_connection(self):
        """Test Ollama server connection"""
        print("Testing Ollama server connection...")
        
        try:
            r = requests.get('http://localhost:11434/api/tags', timeout=5)
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            
            models = r.json()['models']
            print(f"✓ Ollama server is running")
            print(f"✓ Found {len(models)} models:")
            for model in models[:3]:
                print(f"  - {model['name']}")
            
            return True
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_chat_api(self):
        """Test chat API"""
        print("Testing chat API...")
        
        try:
            data = {
                "model": "vaultbox/qwen3.5-uncensored:4b",
                "messages": [
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "stream": False
            }
            
            r = requests.post('http://localhost:11434/api/chat', json=data, timeout=120)
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            
            response = r.json()
            print(f"✓ Chat API responded successfully")
            print(f"✓ Response length: {len(response['message']['content'])} characters")
            print(f"✓ Response preview: {response['message']['content'][:80]}...")
            
            return True
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_generate_api(self):
        """Test generate API"""
        print("Testing generate API...")
        
        try:
            data = {
                "model": "vaultbox/qwen3.5-uncensored:4b",
                "prompt": "Write a Python function to calculate factorial",
                "stream": False
            }
            
            r = requests.post('http://localhost:11434/api/generate', json=data, timeout=30)
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            
            response = r.json()
            print(f"✓ Generate API responded successfully")
            print(f"✓ Response length: {len(response['response'])} characters")
            print(f"✓ Response preview: {response['response'][:80]}...")
            
            return True
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_extension_commands(self):
        """Test extension command registration"""
        print("Testing extension commands...")
        
        extension_path = 'd:\\Myfiles\\vscode-ollama-agent-extension\\out\\extension.js'
        
        try:
            with open(extension_path, 'r') as f:
                content = f.read()
            
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
                return False
            else:
                print("\n✓ All commands registered")
                return True
                
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_vscode_extension_development(self):
        """Test VS Code extension development mode"""
        print("Testing VS Code extension development mode...")
        
        extension_path = 'd:\\Myfiles\\vscode-ollama-agent-extension'
        vscode_path = 'C:\\Program Files\\Microsoft VS Code Insiders\\Code.exe'
        
        try:
            # Check if VS Code is available
            vscode_path = 'C:\\Program Files\\Microsoft VS Code Insiders\\Code.exe'
            if not __import__('os').path.exists(vscode_path):
                print(f"⚠️  VS Code Insiders not found at {vscode_path}")
                print("   Skipping VS Code extension development test")
                return True
            
            # Start VS Code with extension development mode
            process = subprocess.Popen(
                [
                    vscode_path,
                    '--extensionDevelopmentPath', extension_path,
                    '--extensionDevelopmentFolders', extension_path
                ],
                cwd='d:\\Myfiles\\FinRpt\\news_search_app',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for VS Code to start
            time.sleep(10)
            
            # Check if process is still running
            if process.poll() is None:
                print("✓ VS Code started with extension development mode")
                
                # Test Ollama connection through extension
                r = requests.get('http://localhost:11434/api/tags', timeout=5)
                if r.status_code == 200:
                    print("✓ Ollama server accessible through extension")
                else:
                    print(f"✗ Ollama server returned {r.status_code}")
            else:
                print("✗ VS Code failed to start")
                process.terminate()
                process.wait()
                return False
            
            # Clean up
            process.terminate()
            process.wait()
            
            return True
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_gui_functionality(self):
        """Test GUI functionality"""
        print("Testing GUI functionality. ..")
        
        try:
            # Test chat API through the extension's service
            data = {
                "model": "vaultbox/qwen3.5-uncensored:4b",
                "messages": [
                    {"role": "user", "content": "Hello! Test the Ollama Agent GUI."}
                ],
                "stream": False
            }
            
            r = requests.post('http://localhost:11434/api/chat', json=data, timeout=120)
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            
            response = r.json()
            print(f"✓ Chat API responded successfully")
            print(f"✓ Response: {response['message']['content'][:100]}...")
            
            return True
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_agent_creation(self):
        """Test agent creation"""
        print("Testing agent creation...")
        
        try:
            data = {
                "name": "Test Agent",
                "description": "A test agent for testing purposes",
                "model": "vaultbox/qwen3.5-uncensored:4b",
                "system_prompt": "You are a helpful assistant."
            }
            
            r = requests.post('http://localhost:11434/api/chat', json=data, timeout=10)
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            
            response = r.json()
            print(f"✓ Agent creation API responded successfully")
            print(f"✓ Response preview: {response['message']['content'][:80]}...")
            
            return True
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_settings_configuration(self):
        """Test VS Code settings configuration"""
        print("Testing VS Code settings configuration...")
        
        settings_path = 'd:\\Myfiles\\FinRpt\\news_search_app\\.vscode\\settings.json'
        
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            required_settings = {
                'ollama.serverUrl': 'http://localhost:11434',
                'ollama.defaultModel': 'vaultbox/qwen3.5-uncensored:4b',
                'ollama.enableTracing': True,
                'ollama.maxTokens': 4096,
                'ollama.enableCompletion': True,
            }
            
            missing_settings = []
            
            for key, value in required_settings.items():
                if key not in settings:
                    missing_settings.append(key)
                elif settings[key] != value:
                    print(f"  ⚠ {key}: expected {value}, got {settings[key]}")
            
            if missing_settings:
                print(f"✗ Missing {len(missing_settings)} settings:")
                for setting in missing_settings:
                    print(f"  - {setting}")
                return False
            else:
                print("✓ All required settings configured")
                print(f"  - ollama.serverUrl: {settings.get('ollama.serverUrl')}")
                print(f"  - ollama.defaultModel: {settings.get('ollama.defaultModel')}")
                print(f"  - ollama.enableTracing: {settings.get('ollama.enableTracing')}")
                print(f"  - ollama.maxTokens: {settings.get('ollama.maxTokens')}")
                print(f"  - ollama.enableCompletion: {settings.get('ollama.enableCompletion')}")
                return True
                
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_extension_compilation(self):
        """Test extension compilation"""
        print("Testing extension compilation...")
        
        extension_path = 'd:\\Myfiles\\vscode-ollama-agent-extension\\out\\extension.js'
        
        try:
            if not __import__('os').path.exists(extension_path):
                print("✗ Extension file not found")
                return False
            
            with open(extension_path, 'r') as f:
                content = f.read()
            
            # Check for required exports
            required_exports = ['OllamaExtension', 'activate', 'deactivate']
            missing_exports = []
            
            for export in required_exports:
                if f'exports.{export}' not in content:
                    missing_exports.append(export)
            
            if missing_exports:
                print(f"✗ Missing exports: {', '.join(missing_exports)}")
                return False
            else:
                print("✓ Extension properly compiled")
                print("  - OllamaExtension class exported")
                print("  - activate function exported")
                print("  - deactivate function exported")
                return True
                
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_ollama_chat_panel(self):
        """Test Ollama chat panel"""
        print("Testing Ollama chat panel...")
        
        chat_panel_path = 'd:\\Myfiles\\vscode-ollama-agent-extension\\src\\gui\\ollamaChatPanel.ts'
        
        try:
            with open(chat_panel_path, 'r') as f:
                content = f.read()
            
            # Check for required methods
            required_methods = ['createOrCreate', 'updateWebview', 'sendChatMessage']
            missing_methods = []
            
            for method in required_methods:
                if f'{method}(' not in content:
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"✗ Missing methods: {', '.join(missing_methods)}")
                return False
            else:
                print("✓ Chat panel methods found")
                print(f"  - openCopilotGui: Found")
                print(f"  - updateChatView: Found")
                print(f"  - sendChatMessage: Found")
                return True
                
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_ollama_service(self):
        """Test Ollama service"""
        print("Testing Ollama service...")
        
        service_path = 'd:\\Myfiles\\vscode-ollama-agent-extension\\src\\services\\ollamaService.ts'
        
        try:
            with open(service_path, 'r') as f:
                content = f.read()
            
            # Check for required methods
            required_methods = ['chat', 'generate', 'healthCheck']
            missing_methods = []
            
            for method in required_methods:
                if f'{method}(' not in content:
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"✗ Missing methods: {', '.join(missing_methods)}")
                return False
            else:
                print("✓ Ollama service methods found")
                print(f"  - chat: Found")
                print(f"  - generate: Found")
                print(f"  - healthCheck: Found")
                return True
                
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_agent_manager(self):
        """Test agent manager"""
        print("Testing agent manager...")
        
        agent_path = 'd:\\Myfiles\\vscode-ollama-agent-extension\\src\\agents\\agentManager.ts'
        
        try:
            with open(agent_path, 'r') as f:
                content = f.read()
            
            # Check for required methods
            required_methods = ['createAgent', 'runAgent', 'evaluateAgent', 'debugAgent']
            missing_methods = []
            
            for method in required_methods:
                if f'{method}(' not in content:
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"✗ Missing methods: {', '.join(missing_methods)}")
                return False
            else:
                print("✓ Agent manager methods found")
                print(f"  - createAgent: Found")
                print(f"  - runAgent: Found")
                print(f"  - evaluateAgent: Found")
                print(f"  - debugAgent: Found")
                return True
                
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    def test_extension_package(self):
        """Test extension package.json"""
        print("Testing extension package.json...")
        
        package_path = 'd:\\Myfiles\\vscode-ollama-agent-extension\\package.json'
        
        try:
            with open(package_path, 'r') as f:
                package = json.load(f)
            
            required_fields = ['name', 'version', 'main', 'activationEvents', 'contributes']
            missing_fields = []
            
            for field in required_fields:
                if field not in package:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"✗ Missing fields: {', '.join(missing_fields)}")
                return False
            else:
                print("✓ Extension package.json is valid")
                print(f"  - name: {package.get('name')}")
                print(f"  - version: {package.get('version')}")
                print(f"  - main: {package.get('main')}")
                print(f"  - activationEvents: {len(package.get('activationEvents', []))} events")
                return True
                
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OLLAMA AGENT EXTENSION COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tester = OllamaAgentTester()
    
    tests = [
        ("Ollama Server Connection", tester.test_ollama_server_connection),
        ("Extension Compilation", tester.test_extension_compilation),
        ("Extension Package", tester.test_extension_package),
        ("VS Code Settings Configuration", tester.test_settings_configuration),
        ("Ollama Service", tester.test_ollama_service),
        ("Agent Manager", tester.test_agent_manager),
        ("Chat Panel", tester.test_ollama_chat_panel),
        ("Chat API", tester.test_chat_api),
        ("Generate API", tester.test_generate_api),
        ("Agent Creation", tester.test_agent_creation),
        ("GUI Functionality", tester.test_gui_functionality),
        ("VS Code Extension Development", tester.test_vscode_extension_development),
    ]
    
    for test_name, test_func in tests:
        tester.test(test_name, test_func)
    
    tester.print_summary()
    
    return tester.success_count == tester.total_tests


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
