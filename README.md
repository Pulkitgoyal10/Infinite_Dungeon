# The Infinite Dungeon: Adaptive Gamified Learning Platform

[![Live Demo](https://img.shields.io/badge/Live_Demo-Play_Now-00d2ff?style=for-the-badge&logo=streamlit)](https://infinitydungeon1.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Powered_by-Google_Gemini-orange.svg?style=flat&logo=google)](https://aistudio.google.com/)

**The Infinite Dungeon** is an intelligent, highly scalable learning system that dynamically adapts educational challenges based on real-time learner performance. By integrating state-of-the-art Large Language Models (LLMs) with a persistent gamified RPG interface, the platform continuously adjusts difficulty, pacing, and feedback to maximize concept mastery and long-term retention.

---

## 📑 Table of Contents
1. [System Architecture & Capabilities](#-system-architecture--capabilities)
2. [Core Features](#-core-features)
3. [Technical Stack](#-technical-stack)
4. [Installation & Setup](#-installation--setup)
5. [Usage Instructions](#-usage-instructions)
6. [Directory Structure](#-directory-structure)

---

## 🏗 System Architecture & Capabilities

This project implements a unique **Dual-SDK AI Architecture** to handle distinct computational requirements without hallucination or parsing failures:

1. **Algorithmic Evaluation Engine (Modern `google-genai` SDK):** Utilizes GenAI Code Execution Tools (`types.ToolCodeExecution`) to create a secure sandbox. It evaluates user-submitted Python code by generating hidden edge-case test parameters, running the code, and calculating the algorithmic Time Complexity (Big-O notation).
2. **Conceptual Assessment Engine (Legacy `google-generativeai` SDK):** Configured strictly with `response_mime_type="application/json"`. It evaluates the semantic complexity of user-requested subjects (rating them from Tier 1 to Tier 6) and generates unique, unrepeated multiple-choice questions natively in JSON format for seamless frontend rendering.

---

## 🎯 Core Features

* **Dynamic Difficulty Adjustment (DDA):** The AI calculates the academic complexity of any user-submitted topic (e.g., "Basic Addition" vs. "Quantum Mechanics") and dynamically assigns appropriate enemy tiers, health points, and damage outputs.
* **Persistent State Management:** Tracks dynamic player attributes—including Level, Experience Points (XP), Health (HP), and Consumable Inventory—across rendering cycles using Streamlit's session state.
* **Interactive Code IDE:** Integrates `streamlit-ace` for an in-browser code editor featuring syntax highlighting, automated indentation, and real-time execution feedback.
* **Premium Glassmorphism Interface:** Employs advanced custom CSS to deliver a highly responsive, modern UI/UX with smooth transitions, dynamic progress bars, and localized audio triggers (Base64 injected).

---

## 💻 Technical Stack

* **Frontend Framework:** [Streamlit](https://streamlit.io/)
* **Code Editor Component:** `streamlit-ace`
* **AI & LLM Infrastructure:** Google Gemini 2.5 Flash API
* **Environment Variables:** `python-dotenv`

---

## ⚙️ Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.9 or higher installed on your system.

### 2. Clone the Repository
```bash
git clone [https://github.com/Pulkitgoyal10/Infinite_Dungeon.git](https://github.com/Pulkitgoyal10/Infinite_Dungeon.git)
cd infinite-dungeon
