#!/usr/bin/env python3
"""
MediLedger Nexus - Master Test Runner

This script runs all tests across the MediLedger Nexus platform:
- Encryption and security tests
- Zero-Knowledge Proof tests  
- Hedera blockchain tests
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Master test runner for MediLedger Nexus"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.root_dir = self.test_dir.parent
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None
        }
        
    def print_header(self):
        """Print test runner header"""
        print("🧪 MediLedger Nexus - Master Test Runner")
        print("=" * 60)
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Test directory: {self.test_dir}")
        print(f"🏠 Root directory: {self.root_dir}")
        print()
        
    def check_prerequisites(self):
        """Check if prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        prerequisites = {
            'Python': sys.executable,
            'Docker': self.check_docker(),
            'Environment File': self.check_env_file(),
            'Encryption Key': self.check_encryption_key(),
            'Circuits Directory': self.check_circuits_dir(),
            'ZK Directory': self.check_zk_dir()
        }
        
        for name, status in prerequisites.items():
            if status:
                print(f"   ✅ {name}: Available")
            else:
                print(f"   ❌ {name}: Missing")
                
        print()
        return all(prerequisites.values())
        
    def check_docker(self):
        """Check if Docker is available"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
            
    def check_env_file(self):
        """Check if .env file exists"""
        env_file = self.root_dir / '.env'
        return env_file.exists()
        
    def check_encryption_key(self):
        """Check if encryption key is set"""
        return os.getenv('ENCRYPTION_KEY') is not None
        
    def check_circuits_dir(self):
        """Check if circuits directory exists"""
        circuits_dir = self.root_dir / 'circuits'
        return circuits_dir.exists() and any(circuits_dir.glob('*.zok'))
        
    def check_zk_dir(self):
        """Check if zk directory exists"""
        zk_dir = self.root_dir / 'zk'
        return zk_dir.exists()
        
    def run_test_category(self, category, description):
        """Run tests for a specific category"""
        print(f"🧪 Running {description} Tests")
        print("-" * 40)
        
        category_dir = self.test_dir / category
        if not category_dir.exists():
            print(f"   ⚠️ Category directory not found: {category}")
            self.results['skipped'] += 1
            return False
            
        # Find test files
        test_files = list(category_dir.glob('test_*.py'))
        if not test_files:
            print(f"   ⚠️ No test files found in {category}")
            self.results['skipped'] += 1
            return False
            
        category_passed = 0
        category_failed = 0
        
        for test_file in test_files:
            print(f"   🔬 Running {test_file.name}...")
            self.results['total'] += 1
            
            try:
                # Change to category directory for relative imports
                os.chdir(category_dir)
                
                # Run the test
                result = subprocess.run([sys.executable, test_file.name], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"      ✅ PASSED")
                    self.results['passed'] += 1
                    category_passed += 1
                else:
                    print(f"      ❌ FAILED")
                    print(f"         Error: {result.stderr.strip()}")
                    self.results['failed'] += 1
                    category_failed += 1
                    
            except subprocess.TimeoutExpired:
                print(f"      ⏰ TIMEOUT (5 minutes)")
                self.results['failed'] += 1
                category_failed += 1
            except Exception as e:
                print(f"      ❌ ERROR: {e}")
                self.results['failed'] += 1
                category_failed += 1
            finally:
                # Return to test directory
                os.chdir(self.test_dir)
                
        print(f"   📊 {description}: {category_passed} passed, {category_failed} failed")
        print()
        
        return category_failed == 0
        
    def run_demo_tests(self):
        """Run demo tests that don't follow test_*.py naming"""
        print("🎭 Running Demo Tests")
        print("-" * 40)
        
        demo_tests = [
            ('zk_snarks', 'demo_zk_snarks.py', 'ZK-SNARK Demo'),
            ('hedera', 'simple_hedera_test.py', 'Hedera Simple Test')
        ]
        
        for category, filename, description in demo_tests:
            demo_file = self.test_dir / category / filename
            if demo_file.exists():
                print(f"   🎬 Running {description}...")
                self.results['total'] += 1
                
                try:
                    os.chdir(self.test_dir / category)
                    result = subprocess.run([sys.executable, filename], 
                                          capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        print(f"      ✅ PASSED")
                        self.results['passed'] += 1
                    else:
                        print(f"      ❌ FAILED")
                        print(f"         Error: {result.stderr.strip()}")
                        self.results['failed'] += 1
                        
                except Exception as e:
                    print(f"      ❌ ERROR: {e}")
                    self.results['failed'] += 1
                finally:
                    os.chdir(self.test_dir)
            else:
                print(f"   ⚠️ Demo file not found: {filename}")
                self.results['skipped'] += 1
                
        print()
        
    def run_encryption_tests(self):
        """Run encryption tests"""
        return self.run_test_category('encryption', 'Encryption & Security')
        
    def run_zk_snark_tests(self):
        """Run ZK-SNARK tests"""
        return self.run_test_category('zk_snarks', 'Zero-Knowledge Proof')
        
    def run_hedera_tests(self):
        """Run Hedera blockchain tests"""
        return self.run_test_category('hedera', 'Hedera Blockchain')
        
    def print_summary(self):
        """Print test summary"""
        self.results['end_time'] = datetime.now()
        duration = self.results['end_time'] - self.results['start_time']
        
        print("📊 Test Summary")
        print("=" * 60)
        print(f"⏱️  Duration: {duration}")
        print(f"📈 Total Tests: {self.results['total']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⚠️  Skipped: {self.results['skipped']}")
        
        if self.results['total'] > 0:
            success_rate = (self.results['passed'] / self.results['total']) * 100
            print(f"📊 Success Rate: {success_rate:.1f}%")
            
        print()
        
        if self.results['failed'] == 0:
            print("🎉 All tests passed! MediLedger Nexus is ready for deployment.")
        else:
            print(f"⚠️  {self.results['failed']} tests failed. Please review and fix issues.")
            
        print()
        
    def run_all_tests(self):
        """Run all tests"""
        self.results['start_time'] = datetime.now()
        self.print_header()
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Please fix issues and try again.")
            return False
            
        # Run test categories
        print("🚀 Starting test execution...")
        print()
        
        # Run standard test files
        self.run_encryption_tests()
        self.run_zk_snark_tests()
        self.run_hedera_tests()
        
        # Run demo tests
        self.run_demo_tests()
        
        # Print summary
        self.print_summary()
        
        return self.results['failed'] == 0


def main():
    """Main function"""
    # Change to test directory
    test_dir = Path(__file__).parent
    os.chdir(test_dir)
    
    # Load environment variables if .env exists
    env_file = test_dir.parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"')
    
    # Run tests
    runner = TestRunner()
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
