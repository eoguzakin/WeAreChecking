# WeAreChecking working conventions

This project is designed for learning by building.

- Use English for explanations, guides, notebook text, code comments, and feedback.
- Complete infrastructure, bug fixes, and tests autonomously.
- When the user wants to solve exercises together, leave student.py TODOs for that guided work.
- Use a short explanation, a small task, a check, and an interpretation at each step.
- If the user explicitly asks for a solution, provide it without unnecessary permission requests.
- Check both the exercise feedback and the user's interpretation before calling milestones 01 and 02 complete.
- Never present synthetic fixtures as real F1 data.
- Keep target-session results, status, points, and future observed weather out of forecast inputs.
- Use UTC and distinguish observed_at from event time.
- Label historical data downloaded today as reconstructed.
- Keep FP participants separate from race entries; driver_number is not a permanent identity.
- Keep working infrastructure complete outside the designated student.py exercises.
- Keep pyproject and the dependency lock consistent when changing dependencies.
- Validate with: python -m pytest; python scripts/validate_notebooks.py.
- Keep large raw data, .venv, tokens/passwords, caches, and absolute user paths out of commits.
