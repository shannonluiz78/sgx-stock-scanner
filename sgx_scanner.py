name: Run Stock Scanner

on:
  schedule:
    - cron: '0 1 * * 1-5'  # Runs automatically on weekdays
  workflow_dispatch:        # Enables the manual 'Run workflow' button

jobs:
  scan-stocks:
    runs-on: ubuntu-latest
    timeout-minutes: 5      # ⏱️ Safety switch: kills the job if stuck past 5 mins

    permissions:
      contents: write       # 🔑 Gives GitHub permission to save data.json

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Scanner Script
        run: python sgx_scanner.py

      - name: Save Updated Data
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Auto-update stock data [skip ci]"
          file_pattern: "data.json"
