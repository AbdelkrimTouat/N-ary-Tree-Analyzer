# N-ary Tree Analyzer & Complexity Benchmark

![Python](https://img.shields.io/badge/Python-3.x-blue.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg)

A comprehensive Python tool designed to explore, visualize, and analyze **N-ary Trees** (specifically Quadtrees, N=4). 

This project implements core data structure algorithms (Search, Insertion, Deletion, Traversal) and includes a robust **Performance Benchmarking** suite to measure time complexity across varying dataset sizes.

## 🚀 Features

### 1. Visualization & Traversal
* **ASCII Tree Visualization:** Graphically displays the tree structure in the console (similar to the `tree` command).
* **Traversals:** Implements both **Depth-First Search (DFS)** and **Breadth-First Search (BFS)**.

### 2. Core Operations (CRUD)
* **Construction:** Build trees manually, generate random balanced trees, or load preset scenarios (e.g., a File System simulation).
* **Manipulation:** Insert, Modify, and Delete nodes.
    * *Smart Deletion:* Includes logic to handle "orphaned" nodes by promoting grandchildren.
* **Search:** Find nodes by value or calculate the path between two nodes using backtracking.

### 3. Advanced Algorithms
* **Tree Properties:** Calculate Height and check for Completeness (if the tree is filled level-by-level).
* **Max Complete Subtree:** Algorithmic search for the largest "complete" sub-structure within the main tree.
* **N-ary to Binary Transformation:** Converts the N-ary tree into a Binary Tree using the **"Left-Child, Right-Sibling"** representation.

### 4. ⚡ Complexity Benchmarking
A built-in evaluation module (`lancer_evaluation`) that runs automated tests on trees ranging from **10 to 1,000 nodes**. It measures execution time for all operations to demonstrate Big-O complexity (Linear vs. Quadratic behaviors).

## 🛠️ Getting Started

### Prerequisites
* Python 3.x

### Installation
1.  Clone the repository:
    ```bash
    git clone [https://github.com/AbdelkrimTouat/N-ary-Tree-Analyzer.git](https://github.com/AbdelkrimTouat/N-ary-Tree-Analyzer.git)
    ```
2.  Navigate to the directory:
    ```bash
    cd N-ary-Tree-Analyzer
    ```

### Usage
Run the script to start the interactive CLI menu:
```bash
python "Data structure trees and complexity.py"
