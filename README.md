# LogShield – Tamper-Evident Digital Evidence System

## Overview
LogShield is a cybersecurity prototype designed to protect digital activity logs from unauthorized modification or deletion. It helps maintain the integrity of system logs and provides evidence when tampering is detected.

## Problem
In cyberattacks, attackers or malicious insiders may modify or delete activity logs to hide their actions. This makes investigation difficult because logs may no longer be trustworthy.

## Our Solution
LogShield uses cryptographic hashing and hash chaining to make unauthorized changes to stored logs detectable.

## Key Features
- **Activity Logging:** Records sample system activities such as login attempts, file access, and permission changes.
- **SHA-256 Hashing:** Generates a unique hash for each log record.
- **Hash Chaining:** Links records using previous hashes to maintain integrity.
- **Integrity Verification:** Checks whether stored records have been modified.
- **Tamper Simulation:** Demonstrates how changes to a log can be detected.
- **Evidence Export:** Generates a JSON evidence report.

## Technology Used
- Python
- HTML
- CSS
- JavaScript
- SHA-256 Cryptographic Hashing

## Current Prototype
The current version demonstrates log integrity verification using sample logs. It does not yet collect live enterprise or banking logs. Blockchain-based hash anchoring is planned as a future enhancement and is not yet integrated.

## Future Enhancements
- Real-time log collection
- Secure remote log storage
- Blockchain-based hash anchoring
- Automated tampering alerts

## Project Goal
To make digital activity records more trustworthy, verifiable, and useful during cybersecurity investigations.
