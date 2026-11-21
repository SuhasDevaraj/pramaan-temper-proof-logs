LOGSHIELD - READY-TO-RUN HACKATHON PROTOTYPE

START:
1. Extract this ZIP fully.
2. Open the extracted folder.
3. Double-click START_LOGSHIELD.bat.
4. A black terminal window opens and your browser should open at:
   http://127.0.0.1:8000
5. Keep the black terminal window open while using the dashboard.
6. To stop, click the black window and press Ctrl+C.

DEMO FLOW:
1. Click "Load sample logs".
2. Click "Create checkpoint".
3. Click "Simulate attacker".
4. The dashboard should show TAMPERING DETECTED.
5. Click "Export evidence" to download a JSON report.
6. Click "Reset demo" to start again.

REQUIREMENTS:
- Windows 10/11
- Python 3 installed (no extra Python packages required)
- Internet is not required for the app itself; Google Fonts are optional visual styling.

WHAT IT DEMONSTRATES:
- Activity records with SHA-256 hashes.
- Hash chaining: each record references the previous record hash.
- Integrity verification.
- A local checkpoint comparison.
- Simulated log alteration and JSON evidence export.

IMPORTANT TECHNICAL LIMITATION:
This is a functional local prototype, not a deployed blockchain product. The checkpoint is stored locally, so an attacker with full control of the computer could potentially alter both logs and checkpoint. For a production-grade solution, anchor hashes to an independently administered permissioned blockchain or WORM storage, use remote log collection, and protect signing keys separately. Do not claim this prototype already uses blockchain.
