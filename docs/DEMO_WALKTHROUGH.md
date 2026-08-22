# AURA — Agentic Universal Retrieval and Analysis
## System Demonstration & Architectural Walkthrough

> **Tagline**: *Don't search your screenshots. Ask your memory.*  
> **Core Focus**: Multimodal RAG · Knowledge Graph · Zero-Trust Security

---

## The 90-Second Rapid Pitch Script

### [00:00 - 00:15] The Hook: The 4,000 Screenshot Trap
- **Action**: Open the **Gallery** (`http://localhost:3000/gallery`).
- **Narrator**:
  > *"We all take thousands of screenshots — receipts, Wi-Fi passwords, code snippets, research diagrams, travel tickets. But filenames like `Screenshot_2026-08-15_1423.png` make finding anything impossible. Traditional search fails because it looks for text or filenames. We built AURA: an Agentic Visual Memory Engine that doesn't just search screenshots — it understands, connects, protects, and acts on your visual memories."*

---

### [00:15 - 00:35] Demo Query 1: Privacy & AURA Shield
- **Action**: Go to Home (`http://localhost:3000`), enter:
  ```text
  Find my Wi-Fi password
  ```
- **Narrator**:
  > *"Let's test what happens when we ask for sensitive information. Notice what happened immediately: AURA identified the router settings screenshot, but AURA Shield automatically masked the credential with a CRITICAL security alert. The sensitive password is not leaked in search results. Only when I explicitly click 'Reveal' does the verified user see the WPA3 key."*
- **Click**: Click `Reveal` on the redacted card.

---

### [00:35 - 00:55] Demo Query 2: Hybrid Search & Expense Extraction
- **Action**: In the search bar, type:
  ```text
  Find the receipt for my laptop
  ```
- **Narrator**:
  > *"Next, finding an expense. AURA doesn't need the word 'laptop' in the filename. Using our hybrid retrieval algorithm—combining semantic vectors, OCR lexical matching, and category boosting—it instantly retrieves the Amazon ASUS ZenBook receipt as result #1."*
- **Action**: Click on the memory card to open **Memory Detail**. Click **"Extract Expense"** AI Action.
- **Narrator**:
  > *"With one click, AURA extracts structured financial JSON: Merchant (Amazon/Appario), Total (₹1,06,188.20), and GST breakdown."*

---

### [00:55 - 01:15] Demo Query 3: Multi-Step Agentic Investigation
- **Action**: Return to Home, switch to **Investigate** mode, type:
  ```text
  Show me everything related to my computer vision project
  ```
- **Narrator**:
  > *"Now the core agentic capability: 'Show me everything related to my computer vision project'. Watch the live investigation orchestrator: it parsed intent, retrieved candidates, traversed graph relationships, verified evidence, and synthesized a structured answer with connected clusters across YOLO research papers, training logs, bug tracebacks, and ISRO project slides."*

---

### [01:15 - 01:30] Demo Query 4: Visual Memory Constellation
- **Action**: Navigate to **Constellation** (`http://localhost:3000/constellation`).
- **Narrator**:
  > *"Finally, the Memory Constellation. Every screenshot is a node in an organic knowledge graph. Notice the project cluster: Paper → Dataset → Code → Training → Evaluation. Clicking an edge shows why they are connected: shared YOLO entities and temporal proximity."*
- **Conclusion**:
  > *"AURA transforms unsearchable screenshots into an explainable, protected visual memory. Don't search your screenshots. Ask your memory."*

---

## The 5 Guaranteed Verifiable Demo Queries

| # | Prompt | Expected Top Match | Key Feature Proven |
| :--- | :--- | :--- | :--- |
| **1** | `"Find my Wi-Fi password"` | `settings_wifi_password.png` | **AURA Shield**: Auto-masks sensitive WPA3 credentials by default |
| **2** | `"Find the receipt for my laptop"` | `receipt_laptop_amazon.png` | **Hybrid Search**: Ranks ASUS ZenBook purchase #1 + AI Expense Action |
| **3** | `"Show me everything related to my computer vision project"` | Multi-artifact cluster | **Investigation Engine**: Aggregates papers, code, errors, slides into clusters |
| **4** | `"Why did you choose these results?"` | Memory Evidence Drawer | **Evidence Mode**: Cites OCR match, category overlap, and entity confidence |
| **5** | `"Summarize this research screenshot"` | `research_yolo_paper.png` | **AI Actions**: Grounded summary and key facts extraction |
