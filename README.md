<!--
SPDX-FileCopyrightText: 2024 Group 4
SPDX-License-Identifier: CC-BY-NC-SA-4.0
-->

# Signal Analyzer for Marginum Project at UEF
This repository contains the signal processing solution developed as part of the **Industrial Project 2024** at the **University of Eastern Finland**. The application is written in [Python](https://www.python.org) with [PySide6](https://doc.qt.io/qtforpython-6/) and utilizes [SciPy](https://scipy.org/) and [NumPy](https://numpy.org/) for advanced computational tasks.

## Python and Virtual Environments
Python ecosystems offer multiple ways to install and use packages. Here, we recommend using **Anaconda** for managing dependencies. Alternatively, the system Python with **Poetry** for dependency management can be used.

### Setting up a Conda Virtual Environment
- Create a new virtual environment:
conda create -n signal_project python=3.11
- Activate the virtual environment: conda activate signal_project
- Install dependencies: pip install pyside6 scipy numpy

### Setting up a Poetry Virtual Environment
1. Install **Poetry**:pip install poetry

2. Navigate to the project folder and install dependencies:
poetry install

3. Run the application:
poetry run signal_app


---

## Running the Application
Activate the environment and execute the application with the following commands:

### Using Conda:
conda activate signal_project python -m signal_project_main_window

### Using Poetry:
poetry run signal_app


---

## File Tree
- **signal_project**
  - `__init__.py`: Package initialization.
  - `signal_analyzer.py`: Implements the main peak detection and classification algorithm.
  - `signal_app_main_window.py`: Composes the main application window.
  - `signal_app_widget.py`: Main widget for signal visualization.
  - `signal_window_chart_widget.py`: Widget for displaying processed signals.
  - `worker.py`: Constructs worker threads for computation.
  - `worker_signals.py`: Defines signals emitted by worker threads.

- **pyproject.toml**: Project dependencies and configuration for Poetry.
- **README.md**: This file.
- **detections.csv**: Example output file with peak classifications.

---

## Features
1. **Baseline Removal**: Removes low-frequency trends using a moving average convolution.
2. **Peak Detection**: Employs SciPy's `find_peaks()` to identify local maxima.
3. **Peak Classification**: Categorizes peaks into large, medium, or small based on height and prominence.
4. **Graphical User Interface**:
   - Import signal files in CSV format.
   - Visualize signals with detected peaks.
   - Export results to CSV.
5. **Performance**: Processes large datasets in under 10 seconds on a typical machine.

---
