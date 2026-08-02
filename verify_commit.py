#!/usr/bin/env python3
"""
verify_commit.py
~~~~~~~~~~~~~~~~
JARVIS AI OS Commit Verification Suite.
Runs Linting, Type checking, Unit/Integration/E2E tests, and Web metric audits.
"""

import sys
import os
import subprocess
import re

# Setup environment encoding
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_cmd(args, label):
    print(f"\n⚡ Running: {label}...")
    res = subprocess.run(args, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✅ {label} Passed!")
        return True, res.stdout
    else:
        print(f"❌ {label} Failed!")
        print(res.stdout)
        print(res.stderr)
        return False, res.stderr or res.stdout


def get_modified_files():
    try:
        res_cached = subprocess.run(
            ["git", "diff", "--name-only", "--cached"], capture_output=True, text=True
        )
        files = [f.strip() for f in res_cached.stdout.split("\n") if f.strip()]
        if not files:
            res = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
            files = [f.strip() for f in res.stdout.split("\n") if f.strip()]
        return sorted(list(set(files)))
    except Exception:
        return []


def audit_accessibility(html_files):
    print("\n♿ Auditing Accessibility...")
    errors = []
    for f in html_files:
        if not os.path.exists(f):
            continue
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()

        # Check textareas without aria-label
        textareas = re.findall(r"<textarea[^>]*>", content)
        for t in textareas:
            if "aria-label=" not in t:
                errors.append(f"Accessibility Error in {f}: missing aria-label attribute in: {t}")

        # Check inputs without aria-label or label
        inputs = re.findall(r"<input[^>]*>", content)
        for i in inputs:
            if 'type="file"' in i or 'type="submit"' in i or 'type="hidden"' in i:
                continue
            if "aria-label=" not in i and "name=" not in i:
                errors.append(
                    f"Accessibility Error in {f}: missing aria-label/name attribute in: {i}"
                )

    if errors:
        for err in errors:
            print(f"  ❌ {err}")
        return False
    print("✅ Accessibility Audit Passed!")
    return True


def audit_responsiveness(css_files):
    print("\n📱 Auditing Responsive Design Layouts...")
    errors = []
    for f in css_files:
        if not os.path.exists(f):
            continue
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()

        # Check for media queries
        if "@media" not in content:
            errors.append(
                f"Responsiveness Error in {f}: No media queries found. Viewports must be responsive."
            )

    if errors:
        for err in errors:
            print(f"  ❌ {err}")
        return False
    print("✅ Responsiveness Audit Passed!")
    return True


def audit_performance(js_files, css_files):
    print("\n⚡ Auditing Performance Bottlenecks...")
    errors = []

    # Check JS caching / virtual paging
    for f in js_files:
        if not os.path.exists(f):
            continue
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
        if "slice(0," not in content and "pagination" not in content and ".slice" not in content:
            errors.append(
                f"Performance Warning in {f}: Missing client-side virtualization/slicing loops on list outputs."
            )

    # Check CSS GPU Composites
    for f in css_files:
        if not os.path.exists(f):
            continue
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
        if "will-change" not in content and "translate3d" not in content:
            errors.append(
                f"Performance Error in {f}: CSS animations do not utilize GPU hardware-acceleration composites ('will-change', 'translate3d')."
            )

    if errors:
        for err in errors:
            print(f"  ❌ {err}")
        return False
    print("✅ Performance Audit Passed!")
    return True


def main():
    print("==================================================")
    print("🛡️ JARVIS OS PRE-COMMIT VERIFICATION ENGINE 🛡️")
    print("==================================================")

    venv_python = os.path.join(".venv", "Scripts", "python.exe")

    modified = get_modified_files()
    print(f"Modified files detected: {modified}")

    py_files = [f for f in modified if f.endswith(".py")]
    html_files = [f for f in modified if f.endswith(".html")]
    css_files = [f for f in modified if f.endswith(".css")]
    js_files = [f for f in modified if f.endswith(".js")]

    success = True

    # 1. Lint (Ruff + Black)
    if py_files:
        ok, _ = run_cmd(
            [venv_python, "-m", "ruff", "check", "--select=E,F", "--ignore=E501", *py_files],
            "Ruff Linting",
        )
        success = success and ok

        ok, _ = run_cmd(
            [venv_python, "-m", "black", "--check", *py_files], "Black Style Formatting"
        )
        success = success and ok

        # 2. Type Check (Mypy)
        ok, _ = run_cmd(
            [
                venv_python,
                "-m",
                "mypy",
                "--ignore-missing-imports",
                "--explicit-package-bases",
                "--python-version",
                "3.12",
                "--disable-error-code=assignment",
                "--disable-error-code=no-any-return",
                "--disable-error-code=arg-type",
                "--disable-error-code=attr-defined",
                "--disable-error-code=return-value",
                "--disable-error-code=type-var",
                "--disable-error-code=union-attr",
                "--disable-error-code=dict-item",
                "--disable-error-code=var-annotated",
                "--exclude",
                r"\.venv",
                *py_files,
            ],
            "Mypy Type Checking",
        )
        success = success and ok
    else:
        print("\nℹ️ No Python files modified. Skipping Lint and Type Checking.")

    # 3. Unit, Integration, and E2E Tests
    ok, _ = run_cmd(
        [venv_python, "-m", "unittest", "discover", "tests"], "Unified Python Test Suite"
    )
    success = success and ok

    # 4. Responsive Tests
    html_to_audit = html_files if html_files else ["web/index.html", "web/login.html"]
    css_to_audit = css_files if css_files else ["web/styles.css"]
    js_to_audit = js_files if js_files else ["web/app.js"]

    ok = audit_responsiveness(css_to_audit)
    success = success and ok

    # 5. Accessibility Tests
    ok = audit_accessibility(html_to_audit)
    success = success and ok

    # 6. Performance Tests
    ok = audit_performance(js_to_audit, css_to_audit)
    success = success and ok

    print("\n==================================================")
    if success:
        print("🎉 ALL PRE-COMMIT VERIFICATION CHECKS PASSED!")
        print("Ready for safe commit and merge. 🚀")
        print("==================================================")
        sys.exit(0)
    else:
        print("⚠️ SOME VERIFICATION CHECKS FAILED.")
        print("Please resolve the failures reported above before committing. ❌")
        print("==================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
