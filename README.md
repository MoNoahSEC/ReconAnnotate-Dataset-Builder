# 👑 Noah ReconAnnotate Pro — Premium AI Dataset Builder & Defect Tracker

<div align="center">

<!-- Modern Animated SVG Mockup themed in Orange & White (GitHub Native Animation) -->
<svg width="800" height="400" viewBox="0 0 800 400" fill="none" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; height: auto; border-radius: 16px; box-shadow: 0 12px 40px rgba(255,107,0,0.15); border: 2px solid #ff6b00; margin: 20px 0;">
  <!-- Styles for animations -->
  <style>
    @keyframes pulse {
      0% { opacity: 0.3; }
      50% { opacity: 0.8; }
      100% { opacity: 0.3; }
    }
    @keyframes drawBox {
      0%, 100% { stroke-dashoffset: 1000; }
      50% { stroke-dashoffset: 0; }
    }
    @keyframes scan {
      0% { transform: translateY(0); }
      50% { transform: translateY(280px); }
      100% { transform: translateY(0); }
    }
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.2; }
    }
    .grid-line { stroke: #fff0e6; stroke-width: 1; }
    .laser { stroke: #ff6b00; stroke-width: 2; opacity: 0.7; filter: drop-shadow(0 0 4px #ff6b00); animation: scan 6s infinite ease-in-out; }
    .bbox { stroke: #2ecc71; stroke-width: 2; stroke-dasharray: 500; stroke-dashoffset: 500; animation: drawBox 6s infinite ease-in-out; }
    .bbox-defect { stroke: #ff6b00; stroke-width: 2; stroke-dasharray: 500; stroke-dashoffset: 500; animation: drawBox 6s infinite ease-in-out 3s; }
    .tag { fill: #2ecc71; font-family: 'Segoe UI', monospace; font-size: 10px; font-weight: bold; }
    .tag-defect { fill: #ff6b00; font-family: 'Segoe UI', monospace; font-size: 10px; font-weight: bold; }
    .text-ui { fill: #64748b; font-family: 'Segoe UI', sans-serif; font-size: 11px; }
    .text-title { fill: #1e293b; font-family: 'Segoe UI', sans-serif; font-size: 14px; font-weight: bold; }
    .text-logo { fill: #ff6b00; font-family: 'Segoe UI', sans-serif; font-size: 15px; font-weight: 850; letter-spacing: 0.5px; }
    .pulse-dot { fill: #ff6b00; animation: blink 1.5s infinite; }
  </style>

  <!-- Background Card -->
  <rect width="800" height="400" rx="16" fill="#ffffff"/>

  <!-- Titlebar -->
  <rect width="800" height="45" fill="#fafafa" rx="16"/>
  <circle cx="25" cy="22" r="6" fill="#ff5f56"/>
  <circle cx="45" cy="22" r="6" fill="#ffbd2e"/>
  <circle cx="65" cy="22" r="6" fill="#27c93f"/>
  <text x="400" y="28" text-anchor="middle" class="text-title">Noah ReconAnnotate Pro — Premium Workspace Preview</text>

  <!-- Sidebar Left: Classes & Project -->
  <rect x="12" y="55" width="190" height="330" rx="12" fill="#fffaf6" stroke="#ffe0cc" stroke-width="1.5"/>
  <text x="25" y="80" class="text-logo">ReconAnnotate Pro</text>
  <text x="25" y="93" class="text-ui" font-size="8" font-weight="bold" letter-spacing="1">DESIGNED BY NOAH</text>
  
  <!-- Class List Title -->
  <text x="25" y="130" class="text-title" font-size="11">CLASSES (Dataset)</text>

  <!-- Active Class -->
  <rect x="20" y="145" width="170" height="30" rx="15" fill="#ffe0cc"/>
  <rect x="20" y="145" width="6" height="30" rx="3" fill="#ff6b00"/>
  <text x="35" y="164" class="text-ui" fill="#ff6b00" font-weight="bold">0: Defect (Orange)</text>
  <circle cx="170" cy="160" r="4" fill="#ff6b00" class="pulse-dot"/>

  <!-- Class List -->
  <text x="35" y="204" class="text-ui" font-weight="500">1: Good (Green)</text>
  <text x="35" y="239" class="text-ui" font-weight="500">2: Object (Slate)</text>

  <!-- Main Canvas -->
  <rect x="212" y="55" width="576" height="330" rx="12" fill="#fffaf6" stroke="#ffe0cc" stroke-width="1.5"/>
  
  <!-- Canvas Grid -->
  <g opacity="0.5">
    <!-- Horizontal lines -->
    <line x1="212" y1="100" x2="788" y2="100" class="grid-line"/>
    <line x1="212" y1="150" x2="788" y2="150" class="grid-line"/>
    <line x1="212" y1="200" x2="788" y2="200" class="grid-line"/>
    <line x1="212" y1="250" x2="788" y2="250" class="grid-line"/>
    <line x1="212" y1="300" x2="788" y2="300" class="grid-line"/>
    <line x1="212" y1="350" x2="788" y2="350" class="grid-line"/>
    <!-- Vertical lines -->
    <line x1="312" y1="55" x2="312" y2="385" class="grid-line"/>
    <line x1="412" y1="55" x2="412" y2="385" class="grid-line"/>
    <line x1="512" y1="55" x2="512" y2="385" class="grid-line"/>
    <line x1="612" y1="55" x2="612" y2="385" class="grid-line"/>
    <line x1="712" y1="55" x2="712" y2="385" class="grid-line"/>
  </g>

  <!-- Animated Laser Scan Line -->
  <line x1="212" y1="60" x2="788" y2="60" class="laser"/>

  <!-- Simulated Target Object -->
  <rect x="270" y="85" width="460" height="270" rx="8" fill="#ff6b00" opacity="0.04" stroke="#ff6b00" stroke-width="1.5" stroke-dasharray="6 6"/>
  
  <!-- Bounding Box 1 (Good Item) -->
  <rect x="300" y="120" width="160" height="90" class="bbox" fill="none"/>
  <rect x="300" y="98" width="115" height="22" rx="4" fill="#2ecc71"/>
  <text x="305" y="113" class="tag" fill="#ffffff">1: Good [98.5%]</text>
  
  <!-- Bounding Box 2 (Defect Area) -->
  <rect x="520" y="200" width="140" height="110" class="bbox-defect" fill="none"/>
  <rect x="520" y="178" width="120" height="22" rx="4" fill="#ff6b00"/>
  <text x="525" y="193" class="tag-defect" fill="#ffffff">0: Defect [99.2%]</text>

  <!-- Crosshair cursor -->
  <g transform="translate(430, 230)">
    <line x1="-15" y1="0" x2="15" y2="0" stroke="#ff6b00" stroke-width="1.5"/>
    <line x1="0" y1="-15" x2="0" y2="15" stroke="#ff6b00" stroke-width="1.5"/>
    <circle cx="0" cy="0" r="5" stroke="#ff6b00" stroke-width="1" fill="none"/>
  </g>
  
  <!-- Canvas Stats Overlay (Top-Right) -->
  <rect x="660" y="65" width="118" height="60" rx="8" fill="#ffffff" opacity="0.95" stroke="#ffe0cc" stroke-width="1.5"/>
  <text x="670" y="82" class="text-ui" font-size="9" fill="#ff6b00" font-weight="bold">● NOAH ENGINE</text>
  <text x="670" y="97" class="text-ui" font-size="9" font-weight="500">FPS: 144.0 (GPU)</text>
  <text x="670" y="111" class="text-ui" font-size="9" font-weight="500">ZOOM: FIT (100%)</text>
</svg>

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-UI_Framework-green.svg?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/intro)
[![Aesthetics](https://img.shields.io/badge/Aesthetics-Orange_&_White_Luxury-ff6b00.svg?style=for-the-badge)](https://github.com)
[![Creator](https://img.shields.io/badge/Designed_By-NOAH-black.svg?style=for-the-badge&logo=github)](https://github.com)

*A state-of-the-art, ultra-responsive dataset labeling and categorization suite designed natively with `PyQt6` to accelerate bounding-box annotations, polygon masks, freehand shapes, and instant structured dataset exports.*

---

</div>

## 🌟 Introduction & Project Identity

**Noah ReconAnnotate Pro** is a high-performance desktop utility designed to remove bottlenecking from computer vision pipelines. By utilizing a native hardware-accelerated drawing canvas, batch shortcuts, case-insensitive path resolvers, and deferred thumbnail loading, it allows machine learning engineers and dataset annotators to categorize thousands of high-res images and directly export them to structured coordinate directories effortlessly!

> [!IMPORTANT]
> **Why ReconAnnotate Pro?**
> Standard annotators freeze when loading 800+ images from external slow drives. **ReconAnnotate Pro** implements a deferred Timer-queue to load thumbnails dynamically, keeping the UI running at a silky-smooth **144 FPS** at all times!

---

## ⚡ Core Features & Superpowers

*   🎯 **Ultra-Smooth Annotation Canvas:** Draw, scale, and adjust bounding boxes, polygons, and freehand vectors with sub-pixel precision.
*   💾 **Cross-Platform Case-Insensitive Path Resolver:** Automatically repairs case mismatches (`.jpg` vs `.JPG`) and features **Self-Healing Fallback** to resolve displaced files automatically!
*   ⚡ **Turbo-Fast Keyboard Classification:** Categorize whole folders with custom hotkeys and **automatic next-image advance** for lightning speed.
*   🔄 **Image-Scoped Undo/Redo Engine:** Operates isolated local undo/redo stacks to protect image-level annotation histories.
*   🍊 **Premium White & Orange Aesthetic:** Stunning light theme with glassmorphism touches, dapper active widgets, and rounded pill-shaped inputs.
*   🎬 **Built-in Smart Video Splitter:** Extract high-quality dataset frames from standard videos (`.mp4`, `.avi`, `.mov`) automatically.
*   📈 **Instant Dataset Exporter:** Generates split datasets (`images/train`, `images/val`, `labels/train`, `labels/val`) and fully structured `data.yaml` automatically.

---

## 📂 Architecture Map

```text
annotation_tool/
├── 📁 canvas/           # High-precision graphic scene and rendering widgets
│   ├── 📄 items.py       # Custom QGraphicsItem representing annotated boxes & polygons
│   ├── 📄 scene.py       # Intercepts drawing, selections, and bounding calculations
│   └── 📄 view.py        # Zoomable, pan-enabled view container with custom crosshair
├── 📁 export/           # Annotation formatters & splitters
│   ├── 📄 splitter.py    # Splits datasets into train/validation lists
│   └── 📄 dataset_exporter.py # Validates and writes annotations in standardized normalized format
├── 📁 panels/           # Advanced modular interface controls
│   ├── 📄 class_panel.py # Dynamic list of object categories
│   ├── 📄 image_panel.py # Grid previews of batch files with QImageReader speedups
│   ├── 📄 category_panel.py # Image-level classification panel (Good / Bad / Empty)
│   ├── 📄 product_panel.py # Multi-product/batch directory manager
│   └── 📄 toolbar.py     # Rounded tool selection control panel
├── 📁 styles/           # Modern styling configurations (White & Orange Theme QSS)
│   └── 📄 theme.py       # Cohesive style rules for premium interfaces
├── 📁 utils/            # Essential helpers (Autosave, color arrays, path resolvers)
│   ├── 📄 path_resolver.py # Case-insensitive self-healing file locator
│   └── 📄 autosave.py    # Auto-save manager preventing state loss
├── 📄 app.py            # Primary UI assembly and application manager
└── 📄 main.py           # Hardware-scaling entry point
```

---

## 🎹 Heavyweight Productivity Shortcuts

Accelerate your annotation and categorization speeds by **10x** using direct keyboard bindings:

### 🛠️ Mode Selection
| Key Binding | Action |
| :---: | :--- |
| <kbd>B</kbd> | 🟥 **Bounding Box Mode** (Initiates crosshair rectangle tool) |
| <kbd>P</kbd> | ⬡ **Polygon Mode** (Create complex polygons with point-and-click) |
| <kbd>H</kbd> | ✍️ **Freehand Mode** (Draw naturally -> converts to polygon instantly) |
| <kbd>E</kbd> | 🖱️ **Edit Mode** (Select, move, resize, and delete drawings) |

### 🚀 Navigation & Action
| Key Binding | Action |
| :---: | :--- |
| <kbd>Space</kbd> / <kbd>D</kbd> | ➡️ **Next Image** in list |
| <kbd>A</kbd> | ⬅️ **Previous Image** in list |
| <kbd>Ctrl</kbd> + <kbd>S</kbd> | 💾 **Save Project** JSON immediately |
| <kbd>Ctrl</kbd> + <kbd>E</kbd> | 📦 **Export Dataset** to standardized folder structure |
| <kbd>F</kbd> | 🔍 **Fit Image** to fill view perfectly |
| <kbd>Del</kbd> / <kbd>Backspace</kbd> | 💥 **Delete Selected Annotation** instantly |
| <kbd>Ctrl</kbd> + <kbd>Z</kbd> | ↩️ **Undo** last annotation |
| <kbd>Ctrl</kbd> + <kbd>Y</kbd> | ↪️ **Redo** last action |

### ⚡ Turbo-Fast Image Classification (Superpowered)
| Key Binding | Action |
| :---: | :--- |
| <kbd>Ctrl</kbd> + <kbd>1</kbd> | 🟢 Classify as **Good** (Approved) + **Auto-Advance to next photo** 🚀 |
| <kbd>Ctrl</kbd> + <kbd>2</kbd> | 🔴 Classify as **Bad** (Needs Annotation / Defects) |
| <kbd>Ctrl</kbd> + <kbd>3</kbd> | ⚪ Classify as **Empty** (Excluded) + **Auto-Advance to next photo** 🚀 |

---

## 🛠️ Getting Started

### 1. Requirements Installation
Ensure you have **Python 3.8+** installed along with libraries:

```bash
# In the root repository directory
pip install -r requirements.txt
```

### 2. Running the Tool

#### 🚀 Windows Setup (One-Click Launch)
Simply run the optimized executable script in the root directory:
```cmd
run.bat
```

#### 🐧 Linux / macOS Setup
Launch directly via your terminal:
```bash
python main.py
```

---

## 🧑‍💻 Designed & Developed By

<div align="center">

### **Mohamed Abdelrazek (NOAH)**
*AI Engineer, Dataset Specialist & Automation Pioneer*

[![GitHub Follow](https://img.shields.io/github/followers/noah?label=Follow%20NOAH&style=social)](https://github.com)

> *"Supercharging industrial computer vision pipelines and defect datasets with state-of-the-art native desktop systems."*

</div>
