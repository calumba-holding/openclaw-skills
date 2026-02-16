#!/usr/bin/env python3
"""
Test runner for tokenQrusher.

Runs tests without requiring pytest.
"""
import sys
import importlib.util
from pathlib import Path

def load_module_from_path(module_name, file_path):
    """Load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_tests():
    """Run all test modules."""
    test_dir = Path(__file__).parent / 'tests'
    
    test_files = [
        ('classifier', test_dir / 'unit' / 'test_classifier.py'),
        ('optimizer', test_dir / 'unit' / 'test_optimizer.py'),
        ('heartbeat', test_dir / 'unit' / 'test_heartbeat.py'),
        ('edge_cases', test_dir / 'edge' / 'test_edge_cases.py'),
    ]
    
    results = []
    
    for name, path in test_files:
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print('='*60)
        
        # Add scripts to path
        sys.path.insert(0, str(Path(__file__).parent / 'hooks' / 'token-context'))
        sys.path.insert(0, str(Path(__file__).parent / 'scripts' / 'cron-optimizer'))
        sys.path.insert(0, str(Path(__file__).parent / 'scripts' / 'heartbeat-optimizer'))
        
        try:
            module = load_module_from_path(f'test_{name}', path)
            
            # Count test functions
            test_funcs = [f for f in dir(module) if f.startswith('test_')]
            
            print(f"Found {len(test_funcs)} tests in {name}")
            
            passed = 0
            failed = 0
            
            for func_name in test_funcs:
                try:
                    func = getattr(module, func_name)
                    if callable(func):
                        # Check if it's a class (TestClass) or function
                        if func_name.startswith('test_') and not func_name.startswith('test_'):
                            # It's a test class
                            pass
                        else:
                            func()
                            passed += 1
                            print(f"  ✓ {func_name}")
                except Exception as e:
                    failed += 1
                    print(f"  ✗ {func_name}: {e}")
            
            results.append({
                'name': name,
                'passed': passed,
                'failed': failed,
                'total': passed + failed
            })
            
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                'name': name,
                'passed': 0,
                'failed': 1,
                'total': 1
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    
    total_passed = 0
    total_failed = 0
    
    for r in results:
        print(f"{r['name']}: {r['passed']} passed, {r['failed']} failed")
        total_passed += r['passed']
        total_failed += r['failed']
    
    print(f"\nTotal: {total_passed} passed, {total_failed} failed")
    
    return total_failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
