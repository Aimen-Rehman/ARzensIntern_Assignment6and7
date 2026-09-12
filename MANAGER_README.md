# SOAR Playbook Manager System

## Overview
The Playbook Manager coordinates execution modes (on-demand, scheduled, event-driven), tracks execution history, runs system health checks, and handles alerting across multiple security playbooks[span_2](start_span)[span_2](end_span).

## Usage Instructions
1. **List Playbooks:**
   `python playbook_manager.py --list`
2. **Execute a Playbook:**
   `python playbook_manager.py --run phishing-resp-01`
3. **Schedule a Playbook:**
   `python playbook_manager.py --schedule phishing-resp-01 --interval hourly`
4. **Run Health Checks:**
   `python playbook_manager.py --health-check`