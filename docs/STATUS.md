# Status — 3 November 2026

## Ready

- Local Python 3.13 virtual environment and a Jupyter kernel installed inside the repository.
- Windows/Python 3.13 dependency lock; pyproject version ranges for other supported environments.
- Real 2024 Bahrain data: FP1, FP2, FP3, Q, R, with participants, laps, stints, and weather for each session.
- Q and R classifications, with driver-number/abbreviation checks across sources.
- The 2024 Austrian sprint schedule was verified through the API; full sprint data was not downloaded for this setup.
- 21 offline infrastructure tests passed; pip check found no broken requirements in the initial setup.
- Notebooks 01 and 02 were executed from top to bottom. Executed copies and HTML previews are under `reports/executed/`. Git stores notebooks without outputs.
- The notebook HTML previews were inspected in a browser.
- GitHub CI configuration is ready but has not run in a remote repository.
- English guides, notebook explanations, learner feedback, and runtime messages.

## We will complete these together

- [ ] Milestone 1: interpret the tables, implement student.lap_counts, and pass its check.
- [ ] Milestone 2: implement student.qualifying_baseline, save the prediction, and compare it with actual results.
- [ ] Complete the decision note using your own results.

Executing the notebooks without errors does not complete these tasks. No learner prediction or model performance score has been produced yet.

## GitHub

The local Git repository is ready. Target: eoguzakin/WeAreChecking, initially private.
At the end of the initial setup, GitHub sign-in was still pending and the remote repository had not been created.
After sign-in, the existing commits can be pushed without repeating the setup.
