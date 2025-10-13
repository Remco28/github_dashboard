# Spec: Refocus, Simplify, and Enhance

**Date:** 2025-10-13
**Author:** TECHADVISOR
**Status:** READY

## 1. Overview

This document outlines the official plan to pivot the dashboard towards its core value: **providing a fast, minimal-effort way for a user to catch up on their repositories.**

This involves three main tracks of work:
1.  **Decluttering:** Removing distracting features and simplifying the UI.
2.  **Enhancing:** Adding high-value features that directly support the core purpose.
3.  **Foundational Work:** Introducing a testing safety net to ensure long-term quality.

## 2. Priority 1: Quick Wins & Decluttering

*Goal: Immediately improve the focus and utility of the dashboard.*

#### **Task 1.1: Remove Gamification**
- **Action:** Remove the "Motivation" (badges, streaks) and "Nudges" (stale repos) sections from the UI.
- **Implementation:**
    - Delete `services/gamification.py`.
    - Remove all related UI-rendering code from the `ui/` modules.
    - Remove all calls to gamification logic from `app.py`.

#### **Task 1.2: Update `NEXT_STEPS.md` Logic**
- **Action:** Modify the file-fetching logic to support moving `NEXT_STEPS.md` out of the root directory.
- **Implementation:**
    - In `services/next_steps.py`, update the client to first look for the file at `comms/NEXT_STEPS.md`.
    - If it's not found (404 error), it must fall back to checking the root directory (`/NEXT_STEPS.md`) for backward compatibility.

#### **Task 1.3: Add "Last Push Date" to Main Table**
- **Action:** Integrate stale repo information directly into the main repository list, making it more useful and replacing the "Nudges" section.
- **Implementation:**
    - Add a "Last Push" column to the repository table in `app.py`.
    - Ensure the column is sortable.
    - The date should be displayed in a human-readable format (e.g., "3 weeks ago").

#### **Task 1.4: Introduce Basic Testing**
- **Action:** Create a testing foundation to prevent future regressions.
- **Implementation:**
    - Create a `tests/` directory.
    - Add `pytest` to the project dependencies if not already present.
    - Create a `tests/test_analytics.py` file with at least one unit test for a function (e.g., testing streak calculation with mock data).

## 3. Priority 2: Major Usability Enhancements

*Goal: Make the dashboard significantly more interactive and effective.*

#### **Task 2.1: Implement Sorting & Filtering**
- **Action:** Give users control over the repository list.
- **Implementation:**
    - Add a text input box to filter the repository list by name.
    - Add controls to the table headers to allow sorting by multiple columns (Name, Last Push, Open PRs).

#### **Task 2.2: Add Pull Request Data**
- **Action:** Display more valuable data than just the issue count.
- **Implementation:**
    - Update `services/github_client.py` to fetch open Pull Request data.
    - Add an "Open PRs" column to the repository table.
    - Consider highlighting PRs that are awaiting the user's review for extra value.

## 4. Priority 3: Future Feature Spec

*Goal: Design the next major "killer feature."*

#### **Task 3.1: Design "What's New Since Last Visit"**
- **Action:** Begin the design and technical specification for this feature. This is a planning task, not an implementation task.
- **Considerations:**
    - How to store the "last visited" timestamp? (e.g., browser `localStorage`).
    - How to efficiently get the "diff" of what has changed?
    - How to visually represent "new" activity in the UI?

## 5. Documentation Cleanup

- **Action:** Update all project documentation to reflect this new plan.
- **Files to Update:**
    - `docs/ROADMAP.md`
    - `README.md`
    - `docs/ARCHITECTURE.md`