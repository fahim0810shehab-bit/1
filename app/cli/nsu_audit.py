#!/usr/bin/env python3
"""
NSU Academic Audit - CLI Client
Usage:
  python nsu_audit.py login
  python nsu_audit.py upload <file> [--level 3]
  python nsu_audit.py history
  python nsu_audit.py results <transcript_id>
"""

import sys
import os
import json
import requests

API_URL = os.getenv("NSU_API_URL", "http://localhost:8000")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".nsu_token")


def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)


def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None


def api_call(method, endpoint, **kwargs):
    token = load_token()
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{API_URL}{endpoint}"
    resp = requests.request(method, url, headers=headers, **kwargs)
    if not resp.ok:
        print(f"Error: {resp.status_code} - {resp.json().get('detail', 'Unknown error')}")
        sys.exit(1)
    return resp.json()


def cmd_login():
    print("=== NSU Academic Audit - CLI Login ===")
    print("Open your browser and sign in at:", f"{API_URL}")
    print("Then paste your token below (or press Enter to skip):")
    token = input("Token: ").strip()
    if token:
        save_token(token)
        print("Token saved!")
    else:
        print("No token provided. Skipping.")


def cmd_upload(file_path, level=3):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    file_size = os.path.getsize(file_path)
    if file_size > 1024 * 1024:
        print("Error: File too large (max 1MB)")
        sys.exit(1)
    print(f"Uploading {file_path}...")
    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{API_URL}/transcripts/upload",
            headers={"Authorization": f"Bearer {load_token()}"},
            params={"level": level},
            files={"file": (os.path.basename(file_path), f)}
        )
    if not resp.ok:
        print(f"Error: {resp.json().get('detail', 'Upload failed')}")
        sys.exit(1)
    data = resp.json()
    result = data.get("result", {})
    print("\n" + "=" * 60)
    print("  NSU ACADEMIC AUDIT REPORT")
    print("=" * 60)
    print(f"  Program:           {result.get('program', 'Unknown')}")
    print(f"  Major:             {result.get('major', 'N/A')}")
    print(f"  CGPA:              {result.get('cgpa', 0):.2f}")
    print(f"  Standing:          {result.get('academic_standing', 'Unknown')}")
    print(f"  Credits Earned:    {result.get('credits_earned', 0):.1f}")
    print(f"  Credits Remaining: {result.get('credits_remaining', 0):.1f}")
    print(f"  Progress:          {result.get('progress_percent', 0):.1f}%")
    print(f"  Est. Semesters:    {result.get('estimated_semesters', 0)}")
    if result.get("invalid_courses"):
        print(f"\n  ⚠ Invalid Courses: {len(result['invalid_courses'])}")
        for ic in result["invalid_courses"]:
            print(f"    - {ic.get('course_code', 'Unknown')}")
    print("=" * 60)


def cmd_history():
    entries = api_call("GET", "/history")
    if not entries:
        print("No history found.")
        return
    print("\nID  | Filename                          | Program    | Level | CGPA  | Date")
    print("-" * 80)
    for e in entries:
        print(f"{e['id']:<4}| {e.get('filename', 'N/A'):<34}| {e.get('program', 'N/A'):<11}| {e.get('level_used', 3):<6}| {e.get('cgpa', 0):.2f}  | {e.get('timestamp', '')[:10]}")


def cmd_results(transcript_id):
    data = api_call("GET", f"/transcripts/{transcript_id}")
    result = data.get("audit_result", {})
    print("\n" + "=" * 60)
    print("  ACADEMIC AUDIT RESULTS")
    print("=" * 60)
    print(f"  Program:  {result.get('program', 'N/A')}")
    print(f"  CGPA:     {result.get('cgpa', 0):.2f}")
    print(f"  Standing: {result.get('academic_standing', 'N/A')}")
    if result.get("category_progress"):
        print("\n  Category Progress:")
        for cat, info in result["category_progress"].items():
            print(f"    {cat}: {info.get('completed', 0):.1f}/{info.get('required', 0)} ({info.get('percent', 0):.1f}%)")
    if result.get("missing_courses"):
        print(f"\n  Missing Courses ({len(result['missing_courses'])}):")
        for mc in result["missing_courses"][:10]:
            print(f"    - {mc}")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1].lower()
    if cmd == "login":
        cmd_login()
    elif cmd == "upload":
        if len(sys.argv) < 3:
            print("Usage: nsu_audit.py upload <file> [--level N]")
            sys.exit(1)
        file_path = sys.argv[2]
        level = 3
        for i, arg in enumerate(sys.argv):
            if arg == "--level" and i + 1 < len(sys.argv):
                level = int(sys.argv[i + 1])
        cmd_upload(file_path, level)
    elif cmd == "history":
        cmd_history()
    elif cmd == "results":
        if len(sys.argv) < 3:
            print("Usage: nsu_audit.py results <transcript_id>")
            sys.exit(1)
        cmd_results(int(sys.argv[2]))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
