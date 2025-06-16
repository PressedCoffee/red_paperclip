#!/usr/bin/env python3
"""
Red Paperclip Hackathon Final Check
Verifies all components are production-ready for submission
"""

import os
import sys
import json
import glob
from pathlib import Path


def check_requirements():
    """Check if all required files and directories exist."""
    required_files = [
        'README.md',
        'LICENSE',
        'cdp-config.yaml',
        'run_hackathon_demo.py',
        'requirements-dashboard.txt',
        'dashboards/hackathon_dashboard.py'
    ]

    required_dirs = [
        'agents/',
        'cognitive_autonomy_expansion_pack/',
        'negotiation/',
        'trading/',
        'simulation_logs/',
        'receipts/',
        'config/',
        'tests/'
    ]

    print("🔍 Checking required files...")
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file}")

    print("\n🔍 Checking required directories...")
    missing_dirs = []
    for dir in required_dirs:
        if not os.path.exists(dir):
            missing_dirs.append(dir)
        else:
            print(f"✅ {dir}")

    return missing_files, missing_dirs


def check_session_logs():
    """Check session logs exist and are properly formatted."""
    log_dir = 'simulation_logs'
    log_files = glob.glob(os.path.join(log_dir, 'demo_session_*.json'))

    print(f"\n📊 Found {len(log_files)} session logs")

    if not log_files:
        return False, "No session logs found"

    # Check latest log
    latest_log = max(log_files, key=os.path.getctime)
    try:
        with open(latest_log, 'r') as f:
            data = json.load(f)

        event_types = set(event.get('event_type', 'unknown') for event in data)
        print(
            f"✅ Latest log ({os.path.basename(latest_log)}) contains {len(data)} events")
        print(f"   Event types: {', '.join(sorted(event_types))}")
        return True, f"Session logs valid with events: {event_types}"
    except Exception as e:
        return False, f"Error reading session log: {e}"


def check_dashboard_compatibility():
    """Test dashboard can load session logs."""
    try:
        sys.path.insert(0, '.')
        from dashboards.hackathon_dashboard import load_session_logs, analyze_session_metrics

        sessions = load_session_logs()
        if not sessions:
            return False, "Dashboard found no session logs"

        metrics = analyze_session_metrics(sessions[0]['events'])

        print(f"✅ Dashboard loaded {len(sessions)} sessions")
        print(
            f"   Latest session metrics: {metrics['total_events']} events, {metrics['trades_completed']} trades")
        return True, "Dashboard compatibility verified"
    except Exception as e:
        return False, f"Dashboard test failed: {e}"


def check_readme_quality():
    """Check README has key sections."""
    with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()

    required_sections = [
        'Quick Start',
        'x402 Payments',
        'Architecture',
        'Hackathon Submission Checklist',
        'How It Works'
    ]

    missing_sections = []
    for section in required_sections:
        if section.lower() not in readme.lower():
            missing_sections.append(section)
        else:
            print(f"✅ README contains '{section}' section")

    return len(missing_sections) == 0, missing_sections


def recommend_cleanup():
    """Recommend files/directories that could be cleaned up."""
    cleanup_candidates = [
        'dev/',
        'docs/',
        'backend_api/',
        '__pycache__/',
        '.pytest_cache/',
        'chaos_pack/',  # If not essential
        '*.pyc'
    ]

    existing_cleanup = []
    for candidate in cleanup_candidates:
        if os.path.exists(candidate):
            existing_cleanup.append(candidate)

    if existing_cleanup:
        print(f"\n🧹 Recommended for cleanup/archiving:")
        for item in existing_cleanup:
            print(f"   - {item}")

    return existing_cleanup


def main():
    print("🚀 Red Paperclip Hackathon Final Check")
    print("=" * 50)

    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    all_checks_passed = True

    # Check requirements
    missing_files, missing_dirs = check_requirements()
    if missing_files or missing_dirs:
        print(f"❌ Missing files: {missing_files}")
        print(f"❌ Missing directories: {missing_dirs}")
        all_checks_passed = False

    # Check session logs
    logs_ok, logs_msg = check_session_logs()
    if not logs_ok:
        print(f"❌ Session logs: {logs_msg}")
        all_checks_passed = False
    else:
        print(f"✅ {logs_msg}")

    # Check dashboard
    dash_ok, dash_msg = check_dashboard_compatibility()
    if not dash_ok:
        print(f"❌ Dashboard: {dash_msg}")
        all_checks_passed = False
    else:
        print(f"✅ {dash_msg}")

    # Check README
    readme_ok, readme_missing = check_readme_quality()
    if not readme_ok:
        print(f"❌ README missing sections: {readme_missing}")
        all_checks_passed = False
    else:
        print("✅ README contains all required sections")

    # Cleanup recommendations
    cleanup_items = recommend_cleanup()

    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 ALL CHECKS PASSED - READY FOR HACKATHON SUBMISSION!")
        print("\n📋 Final Steps:")
        print("   1. Archive/remove cleanup candidates if desired")
        print("   2. Git tag as v1.0-hackathon")
        print("   3. Push to GitHub")
        print("   4. Submit to hackathon")
    else:
        print("❌ SOME CHECKS FAILED - FIX ISSUES BEFORE SUBMISSION")

    return all_checks_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
