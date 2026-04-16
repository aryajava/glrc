# GLRC Contributing Guidelines

Welcome to the **GLRC** ecosystem! We are thrilled that you are considering investing your time and code to expand this project.
Processing and managing hundreds of GitLab repositories is no easy feat, and your contribution will tremendously help other developers breeze through their daily tasks.

This document serves as the official guideline to ensure your Pull Request (PR) pipeline remains secure, organized, and easily maintainable.

---

## 1. Reporting Bugs & Errors
Even the greatest of software has its flaws. If you encounter abnormal UI freezes, exception tracebacks, or unexpected force closes, please help us squash them.

**Before Creating an Issue:**
1. Check the [Issues](https://github.com/aryajava/glrc/issues) board and initiate a generic keyword search. Ensure no one else has already reported the exact bug.
2. Utilize the **latest stable release** of GLRC. It is highly probable the bug you encountered was already patched in the previous minor/patch version.

**How to Report:**
1. Open our GitHub repository, hit `New Issue`.
2. Select the **Bug Report** template.
3. **Important:** Ensure you explicitly provide the "Steps to Reproduce". For instance: *"Click button A, insert value B, and the application freezes"*. Providing actionable tracing will infinitely speed up our debugging process.

---

## 2. Requesting Features (Enhancements)
Have a brilliant feedback or an idea to make GLRC more powerful? 
Utilize the **Feature Request** template. Describe your exact daily *pain point* and map out what the conceptual blueprint feature should act like to solve your problem.

---

## 3. Local Setup & Sending a Pull Request (PR)

GLRC is natively written utilizing a **Python** core and a UI shell wrapped around **CustomTkinter**. Please maintain the integrity of our code.

### A. Local Environment Setup
1. Fork this repository into your personal GitHub namespace.
2. Clone it unto your local machine.
3. Isolate the environment by establishing a Virtual Environment (Venv) to prevent dependency conflicts with your system packages:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate   # Linux / Mac
   ```
4. Install all prerequisites:
   ```bash
   pip install -r requirements.txt
   ```

### B. Core Code Style Standard
- **Avoid God Classes:** Substantially avoid throwing all massive logic operations entirely onto `main.py`! Architect them cleanly and distribute them thoroughly under the `/src/...` subsystems to keep it modular.
- **Bilingual Interface Commitment:** If you append or engineer brand new contextual texts for our UI elements (Example: adding a new exception prompt dialogue), you **MUST** map and translate them directly inside the `src/utils/i18n.py` file. It is radically forbidden to literally hardcode English/Indonesian strings bare-naked into UI files!

### C. Pull Request Procedure
Ready to showcase your blazing fast logic patch?
1. Please do not commit straight onto the `main` branch. Architect your code on an isolated feature branch.
   > ❌ Bad Practice: `git checkout main` \
   > ✅ Good Practice: `git checkout -b feature/cancel-btn`
2. Push your localized commit into your forked repository and hit the **Pull Request (PR)** submission format.
3. Fill down the dynamic PR Checklist template. Assure and check (✓) all necessary boxes promising that your code does not invoke breaking regressions and was successfully tested cross-platform natively natively on your OS architecture.

---

## 4. Contributor Wall of Fame
Within the Open-Source engineering realm, absolute recognition serves as the main currency. All authors holding successfully merged PRs will be automatically catalogued into our official project history credit tree.

Let's ascend the developer hierarchy and optimize corporate GitLab processing!
