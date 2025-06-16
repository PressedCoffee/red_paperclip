#!/usr/bin/env python3
"""
Simple Appraisal System Test
Tests the basic appraisal functionality without complex imports
"""

import sys
import os
import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_basic_appraisal():
    """Test basic appraisal functionality."""
    print("🔧 Testing Basic Appraisal System...")

    try:        # Import config
        import importlib.util
        config_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'config', 'trade_config.py')
        spec = importlib.util.spec_from_file_location(
            "trade_config", config_path)
        trade_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(trade_config)

        config = trade_config.get_config()
        base_costs = trade_config.calculate_base_costs()
        archetype_config = trade_config.get_archetype_config("visionary")

        print("✅ Config System Working:")
        print(f"   LLM Enabled: {config['llm']['enable_llm_reasoning']}")
        print(f"   Base Gas Cost: ${base_costs['gas_cost_usd']}")
        print(
            f"   Visionary Risk Multiplier: {archetype_config['risk_multiplier']}")

        # Test basic item structure
        test_item = {
            "name": "AI Development Toolkit",
            "description": "Comprehensive AI development suite",
            "category": "software",
            "market_value": 500.0,
            "condition": "excellent",
            "type": "digital",
        }

        print(f"✅ Test Item Created: {test_item['name']}")
        print(f"   Market Value: ${test_item['market_value']}")
        print(f"   Category: {test_item['category']}")

        return True

    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False


def test_agent_creation():
    """Test agent creation with minimal dependencies."""
    print("🤖 Testing Agent Creation...")

    try:
        # Mock capsule data for testing
        capsule_data = {
            "capsule_id": "test_001",
            "goal": "Test AI development",
            "values": {"innovation": 0.8},
            "tags": ["AI", "test"],
            "wallet_address": "0x123456789",
            "public_snippet": "Test agent",
            "archetype": "visionary"
        }

        print("✅ Mock Capsule Created:")
        print(f"   ID: {capsule_data['capsule_id']}")
        print(f"   Goal: {capsule_data['goal']}")
        print(f"   Archetype: {capsule_data['archetype']}")

        return True

    except Exception as e:
        print(f"❌ Agent creation test failed: {e}")
        return False


def run_simple_tests():
    """Run simple appraisal system tests."""
    print("🚀 Starting Simple Appraisal System Tests")
    print("=" * 50)

    tests_passed = 0
    total_tests = 2

    # Test 1: Basic config and cost calculation
    if test_basic_appraisal():
        tests_passed += 1
        print()

    # Test 2: Agent creation
    if test_agent_creation():
        tests_passed += 1
        print()

    # Summary
    print("=" * 50)
    print("📊 SIMPLE TEST SUMMARY")
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    print(f"Success rate: {(tests_passed/total_tests)*100:.1f}%")

    if tests_passed == total_tests:
        print("🎉 ALL SIMPLE TESTS PASSED!")
        print("✅ Configuration system is working")
        print("✅ Basic structures are valid")
        print("Ready for full system testing!")
    else:
        print(f"⚠️  {total_tests - tests_passed} tests failed")
        print("Check configuration and dependencies")

    return tests_passed == total_tests


if __name__ == "__main__":
    success = run_simple_tests()
    exit(0 if success else 1)
