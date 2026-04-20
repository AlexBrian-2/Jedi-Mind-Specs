# Research Orchestrator - Complete Setup & Usage Guide

This document provides step-by-step instructions for setting up, installing, configuring, and using the Research Orchestrator application. Every detail is explained - if something seems obvious, it still has instructions. This guide assumes zero prior knowledge.

---

## Table of Contents

1. [What Is This Application?](#1-what-is-this-application)
2. [What Do You Need Before Starting](#2-what-do-you-need-before-starting)
3. [Installing Python](#3-installing-python)
4. [Getting The Code](#4-getting-the-code)
5. [Installing Dependencies](#5-installing-dependencies)
6. [Understanding The Application](#6-understanding-the-application)
7. [Starting The Application](#7-starting-the-application)
8. [Using The Application](#8-using-the-application)
9. [Understanding The Results](#9-understanding-the-results)
10. [Troubleshooting Common Problems](#10-troubleshooting-common-problems)
11. [Advanced Configuration](#11-advanced-configuration)
12. [Uninstalling / Starting Over](#12-uninstalling--starting-over)

---

## 1. What Is This Application?

Research Orchestrator is a **desktop application** that helps you research any project you want to build (a website, mobile app, desktop program, API, etc.).

Here's how it works:

1. You tell it what kind of project you want to create
2. It uses 20 artificial intelligence "agents" to research different aspects
3. Each agent specializes in one area (frontend design, backend architecture, database, auth, planning, etc.)
4. The agents work together following a strict workflow
5. At the end, you get detailed specification documents

Think of it like having 20 expert consultants who each research a specific part of your project, then compile their findings into a comprehensive blueprint.

### Why Is This Useful?

Instead of spending hours Googling different aspects of your project, the system does the research for you automatically. You get:

- Wireframe and layout recommendations
- UI component library suggestions
- Color and style guides
- Backend architecture patterns
- Database recommendations
- Authentication approaches
- Technology stack recommendations
- Project timelines
- Architecture diagrams
- Best practices guides
- Reviews of everything
- Final validation

---

## 2. What Do You Need Before Starting

Before you begin, make sure you have:

| Requirement | What It Means | How To Check |
|-------------|---------------|--------------|
| A computer | Any laptop or desktop computer | - |
| Internet connection | WiFi or ethernet cable | Can you open a website? |
| Admin rights | Ability to install software | Can you install programs on this computer? |
| Python 3.10 or newer | Programming language | See Section 3 |

---

## 3. Installing Python

Python is the programming language this application is written in. You need to install it first.

### Windows Instructions

1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Go to: https://www.python.org/downloads/
3. Click the button that says "Download Python 3.12.x" (or the newest version)
4. Wait for the file to download (might take a few minutes)
5. Open the downloaded file (usually in your Downloads folder)
6. **IMPORTANT**: Check the box that says "Add Python to PATH"
7. Click "Install Now"
8. Wait for installation to complete
9. Close the installer

### macOS Instructions

Option A - Using Homebrew (Recommended if you have Homebrew):

1. Open Terminal (Applications > Utilities > Terminal)
2. If you don't have Homebrew, install it by pasting:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Enter your password when asked
4. After it installs, run:
   ```
   brew install python
   ```

Option B - Direct Download:

1. Open your web browser
2. Go to: https://www.python.org/downloads/
3. Click "Download Python 3.12.x"
4. Open the downloaded file
5. Follow the installation prompts
6. Close the installer

### Linux (Ubuntu/Debian) Instructions

1. Open Terminal
2. Run these commands one at a time:
   ```
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```
3. Enter your password when asked

### Verify Python Is Installed

1. Open Terminal (Linux/macOS) or Command Prompt (Windows)
2. Type exactly:
   ```
   python --version
   ```
3. Press Enter
4. You should see something like "Python 3.12.0" - the numbers might be different but should start with "3.1" or "3.12"

If you see "Python 3.10.0" or newer, you're good to go!

---

## 4. Getting The Code

The code is the collection of files that make up the application. You need to get these files onto your computer.

### Step-by-Step:

1. Create a new folder on your computer where you want the application to live
   - Example: Create a folder called "ResearchApp" in your Documents folder
   
2. The code files should be provided to you. Assuming you have received this as a zip file or folder:

#### If You Received a ZIP File:

1. Find the zip file (probably in your Downloads folder)
2. Right-click on it
3. Select "Extract All" (Windows) or double-click (macOS)
4. Choose the folder you created as the destination
5. Click Extract

#### If You Received a Folder:

1. Copy the entire folder
2. Paste it into the location you created in step 1

### Verify You Have All The Files

Open the folder and confirm you see these files/folders inside:

- `main.py` - The main entry point
- `requirements.txt` - List of dependencies
- `core/` - Core functionality folder
- `gui/` - Graphical interface folder
- `tools/` - Research tools folder
- `tests/` - Tests folder

---

## 5. Installing Dependencies

Dependencies are other people's code libraries that this application needs to function. They're listed in `requirements.txt`.

### Windows Instructions

1. Open Command Prompt:
   - Press Windows key + R
   - Type "cmd"
   - Press Enter

2. Navigate to the application folder:
   - Type: `cd %USERPROFILE%\Documents\ResearchApp`
   - (Replace "ResearchApp" with whatever you named your folder)
   - Press Enter

3. Install the dependencies:
   - Type: `pip install -r requirements.txt`
   - Press Enter
   - Wait for installation to complete (might take 5-10 minutes)
   - You might see warnings - that's okay, don't worry about them

### macOS / Linux Instructions

1. Open Terminal

2. Navigate to the application folder:
   - Type: `cd ~/Documents/ResearchApp` (macOS)
   - Or: `cd ~/ResearchApp` (Linux)
   - Press Enter

3. Install the dependencies:
   - Type: `pip3 install -r requirements.txt`
   - Press Enter
   - Wait for installation to complete

### What If pip Doesn't Work?

Try using `python -m pip` instead:

**Windows:**
```
python -m pip install -r requirements.txt
```

**macOS/Linux:**
```
python3 -m pip install -r requirements.txt
```

### Verification

To verify dependencies installed correctly:

1. Type: `pip list` (or `pip3 list`)
2. Press Enter
3. You should see a long list of installed packages

Look for these key packages in the list:
- PySide6
- litellm
- crewai
- duckduckgo-search
- sqlalchemy

If all are present, you're ready to go!

---

## 6. Understanding The Application

Before you run it, let's understand what you're looking at.

### The Agent Hierarchy

The application uses 20 AI agents organized in a hierarchy:

```
Master Agent (Tier 1)
├── Frontend Lead (Tier 2)
│   ├── Wireframe & Layout Specialist
│   ├── UI Components Specialist
│   ├── Color & Style Specialist
│   └── UX Specialist
├── Backend Lead (Tier 2)
│   ├── Primary Backend Specialist
│   ├── Database Specialist
│   └── Auth Specialist
├── Specs Lead (Tier 2)
│   ├── Spec Documents Specialist
│   ├── Tech Stack Specialist
│   ├── Planning Specialist
│   ├── Architecture Specialist
│   └── Best Practices Specialist
├── Review Lead (Tier 2)
│   ├── Review Agent #1
│   ├── Review Agent #2
│   └── Review Agent #3
└── Validation Lead (Tier 2)
    ├── Validation Agent #1
    └── Validation Agent #2
```

Each agent researches one specific aspect of your project.

### The Workflow

The application follows a specific workflow:

1. **IDLE** - Waiting for you to start
2. **PARSING** - Analyzing your request
3. **RESEARCH** - Agents research different aspects (happens in batches)
4. **REVIEW** - Review agents check the work
5. **VALIDATION** - Validation agents do final checks
6. **COMPLETE** - Everything finished

### The GUI Layout

The application window has four main areas:

| Area | What It Shows |
|------|-------------|
| Left Panel | Project configuration form |
| Center-Top | Live agent hierarchy with status |
| Center-Bottom | Real-time activity log |
| Right Panel | Generated specification documents |
| Bottom Bar | Rate limit status (API usage) |

---

## 7. Starting The Application

### Windows

1. Open Command Prompt
2. Navigate to the application folder:
   ```
   cd %USERPROFILE%\Documents\ResearchApp
   ```
3. Run the application:
   ```
   python main.py
   ```
4. Press Enter

### macOS

1. Open Terminal
2. Navigate to the application folder:
   ```
   cd ~/Documents/ResearchApp
   ```
3. Run the application:
   ```
   python3 main.py
   ```
4. Press Enter

### Linux

1. Open Terminal
2. Navigate to the application folder:
   ```
   cd ~/ResearchApp
   ```
3. Run the application:
   ```
   python3 main.py
   ```
4. Press Enter

### What Should Happen

A new window should appear on your screen with:

- A header saying "Research Orchestrator - Hierarchical Multi-Agent System"
- Left panel with form fields
- Center panel with agent tree (initially all showing "IDLE" status)
- Right panel showing welcome message
- Bottom status bar

### If It Doesn't Work

See Section 10: Troubleshooting Common Problems

---

## 8. Using The Application

Now let's actually use it to research a project.

### Step 1: Fill In Project Name

1. In the left panel, find the "Project Name" field
2. Click on it
3. Type a name for your project
   - Example: "My Awesome App"
   - Use letters, numbers, and spaces only
   - Don't use special characters like !@#$%^&*

### Step 2: Select Project Type

1. Find the "Project Type" dropdown
2. Click on it
3. Select the type that matches what you want to build:

| If You Want To Build... | Select... |
|----------------------|-----------|
| A website | Web Application |
| A phone app | Mobile Application |
| A computer program | Desktop Application |
| A backend service/API | API / Backend Service |
| A command-line tool | CLI Tool |
| Data processing system | Data Pipeline |
| AI/ML system | ML / AI System |
| Something else | Other |

### Step 3: Write Project Description

This is the most important part. The more detail you provide, the better the research will be.

1. Find the "Description" text area
2. Write at least 100 characters (letters, spaces, punctuation)
3. Include:
   - What your project does
   - Who it's for
   - Key features
   - Any technical requirements

**Example Description:**
```
I want to build a task management app for small teams. It should let users create tasks,
assign them to team members, set due dates, and track progress. The app needs
user authentication, real-time updates, and a clean intuitive interface.
Target users are small businesses and remote teams.
```

### Step 4: Configure Advanced Settings (Optional)

Click "Advanced Settings" to expand this section:

| Setting | What It Does | Default |
|---------|-------------|---------|
| Model | Which AI model to use | Kilo Auto Free (recommended) |
| Max Review Cycles | How many times reviewers can request changes | 3 |
| Max Validation Cycles | How many times validators can check | 2 |
| Inter-call Delay | Wait time between API calls (milliseconds) | 2000 (2 seconds) |

The defaults work fine for most cases. Only change these if you know what you're doing.

### Step 5: Start The Research Run

1. Double-check all fields are filled in
2. Make sure description is at least 100 characters
3. Click the "Start Research Run" button
4. Wait...

### Step 6: Watch The Progress

The application window will update:

- **Run Status**: Shows "Running" (top right)
- **Workflow State**: Shows current phase (bottom left of status bar)
- **Agent Tree**: Agents change from IDLE → ACTIVE (green) → COMPLETE (blue)
- **Activity Log**: Shows what's happening in real-time
- **Spec Documents**: New tabs appear as agents finish

### Step 7: View Results

When COMPLETE, the right panel shows all generated documents:

- Click on any tab to view that spec document
- Documents are saved to the `output/` folder in your application folder
- The master report combines everything

### To Stop Early

Click "Cancel Run" to stop anytime. Your results up to that point are saved.

---

## 9. Understanding The Results

After a run completes, you get specification documents in the `output/` folder.

### Default Output Files

| File | What It Contains |
|------|--------------|
| master_spec_[projectname].md | Combined report of everything |
| wireframe_spec.md | Layout recommendations |
| components_spec.md | UI component suggestions |
| style_spec.md | Color and style guide |
| ux_spec.md | User experience recommendations |
| backend_spec.md | Backend architecture |
| database_spec.md | Database recommendations |
| auth_spec.md | Authentication approach |
| techstack_spec.md | Technology recommendations |
| planning_spec.md | Project timeline |
| architecture_spec.md | System architecture |
| bestpractices_spec.md | Coding standards |

### Reading The Documents

Each document follows this structure:

```
# Document Title

**Project**: Your project name
**Generated**: Date and time
**Agent**: Which agent created this
**Confidence**: How sure the agent is (High/Medium/Low)

---

## Executive Summary
Brief overview

## Detailed Section
Detailed information

## Sources
Where the agent found information
```

---

## 10. Troubleshooting Common Problems

### Problem: "python is not recognized"

**Solution:** Python isn't in your PATH. Try:

Windows:
```
C:\Python312\python.exe main.py
```
(Replace with the actual path where Python is installed)

Or reinstall Python and check "Add Python to PATH".

### Problem: "No module named 'PySide6'"

**Solution:** Dependencies didn't install. Run:

```
pip install -r requirements.txt
```

### Problem: Window doesn't appear

**Solution:** 
- Make sure you're running from the correct folder
- Try running with `-i` flag to see errors:
  ```
  python main.py 2>&1
  ```

### Problem: Application crashes immediately

**Solution:** 
1. Check Python version: `python --version` (needs 3.10+)
2. Reinstall dependencies: `pip install -r requirements.txt`

### Problem: "Rate limit exceeded"

**Solution:** You're using too many API calls. Wait an hour for the limit to reset. The rate limiter should handle this automatically.

### Problem: Web search doesn't work

**Solution:** 
- Check your internet connection
- DuckDuckGo search should work without API keys
- Tavily needs an API key (optional - DuckDuckGo is fallback)

### Problem: Window looks wrong/ugly

**Solution:**
- The application uses system Qt theme
- On Windows, it looks like Windows
- On macOS, it looks like macOS
- This is normal

---

## 11. Advanced Configuration

### Changing The Model

In Advanced Settings, you can change which AI model is used:

| Model | Pros | Cons |
|-------|------|------|
| kilo/auto-free | Free, works well | May be slower |
| gpt-4o | Powerful | Uses credits |
| claude-sonnet-4 | Great reasoning | Uses credits |

### Setting Up Tavily (Optional)

Tavily provides better search results but needs an API key:

1. Go to https://tavily.com/
2. Sign up for an account
3. Get your API key
4. Update the code to use your key

### Custom Output Location

Find this line in `tools/doc_generator.py`:
```python
self.output_dir = "./output"
```
Change `"./output"` to your preferred folder path.

### Adjusting Rate Limits

In `core/rate_limiter.py`, find:
```python
soft_limit: int = 180
```

Change `180` to your preferred limit (remember: 200/hour is the hard limit).

### Running Tests

To run the included tests:

```
cd ~/Documents/ResearchApp
python -m pytest tests/ -v
```

---

## 12. Uninstalling / Starting Over

### Want To Start Fresh?

1. Delete the application folder
2. Delete any output folders created
3. Start from Section 4 again

### Want To Keep Results But Reset?

1. Close the application
2. Copy your results somewhere safe
3. Delete the application folder
4. Start fresh

### Uninstalling Python (Usually Not Recommended)

**Windows:**
1. Open Control Panel > Programs and Features
2. Find Python in the list
3. Right-click > Uninstall

**macOS:**
```
brew uninstall python
```

**Linux:**
```
sudo apt remove python3 python3-pip
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Navigate to folder | `cd ~/Documents/ResearchApp` |
| Install dependencies | `pip install -r requirements.txt` |
| Run application | `python main.py` |
| Run tests | `python -m pytest tests/ -v` |
| Check Python version | `python --version` |
| Check installed packages | `pip list` |

---

## Getting Help

If you need help:

1. Check this document again
2. Check the README.md
3. Look at the code comments in the files
4. Check online documentation for the tools used

---

## Document Information

- Version: 1.0
- Application: Research Orchestrator
- Specification: Jedi Mind Specs v2.0
- Last Updated: 2026-04-20

Happy researching!