# Macro_Tree

⚠️ This project is under continuous refactoring and enhancement, including data structures, classes, CI, and documentation. The demo may be partially incomplete.

A tree-based macro management application.

While developing a macro program for a 3D AI data construction project in the workplace, I experienced the limitations of one-off software and the difficulty of internalizing technical skills. To address this, I started a boilerplate project focused on reusability and extensibility. Retaining only the macro concept, I rebuilt the system around a basic tree structure, emphasizing generality, flexibility, and robustness.

---

## Demo

<table>
  <tr>
    <td align="center">
      <strong>Before (2023)</strong><br>
      <img src="src/images/demo/before.gif" alt="Before" height="400"/>
    </td>
    <td align="center">
      <strong>After (2025, in progress)</strong><br>
      <img src="src/images/demo/after.gif" alt="After" height="400"/>
    </td>
  </tr>
</table>

---

## Project History

| Item | 2022 (Work) | 2023 (Theory/Learning) | 2025 (Application) |
|------|-------------|-----------------------|-------------------|
| Motivation | Self-initiated during work | Personal learning project | General-purpose open source tool |
| Publication | Private (team use) | Public (GitHub) | Public (GitHub) |
| Target Users | Team members | General users | Developers |
| Purpose | 3D AI data construction automation | Learning prototype | Open source SW |
| Key Feature | Macro automation | Command composition automation | Development assistance |
| Data Structure | Simple/None | Tree structure | Tree structure |
| Framework | PyQt5 | PyQt6 | PyQt6 (+cross-platform) |
| UX/UI | Compact | All-in-one | All-in-one |

The 2022 version was a self-initiated internal tool built only with open-source libraries. (No company code or infrastructure was used.)

## Technology & Quality Improvement Status

This table summarizes the adoption of major design, quality, automation, and AI assistance in the Macro_Tree project as of 2023 (initial) and 2025 (final).

| Item                  | Before (2023) | After (2025) | Details |
|-----------------------|:-------------:|:------------:|:--------|
| Design Principles     | 🟡            | 🟢           | SOLID principles (SRP, OCP, LSP, ISP, DIP) |
| Modern Python Paradigms | ❌          | 🟢           | Type hinting, Protocol/Interface, Data Class, etc. |
| Design Patterns       | 🟡            | 🟢           | Observer, Repository, State, Singleton, Factory, Command, Adapter, Memento |
| Architecture Pattern | ❌      | 🟢           | MVVM (Core-Model-ViewModel-Platforms(Adapter)-View) |
| Test/Quality Management | ❌         | 🟢           | pytest, mypy, CI, flake8 |
| Documentation         | 🟡            | 🟢           | README, pdoc, diagrams |
| AI Assistance     | ❌            | 🟢           | Cursor |

---

## Key Feature Implementation Status

| Feature           | Before (2023) | After (2025) | Details |
|-------------------|:-------------:|:------------:|:--------|
| Tree              | 🟢            | 🟢           | Add/Delete/Move tree nodes |
| Undo/Redo(Custom) | 🟢            | 🟢           | State history and restoration |
| Action Data       | 🟢            | 🔄           | Device-specific actions |
| Save/Load         | 🟢            | 🔄           | Save/Load |
| Database          | ❌            | 🔄           | PostgreSQL |
| Grouping          | 🟢            | ❌           | Group/Ungroup |
| Checkbox          | 🟢            | ❌           | Checkbox integration |
| Get Mouse Position| 🟢            | ❌           | Continuous mouse coordinate acquisition |
| Menu              | 🟢            | ❌           | Menubar, Context menu |

---

## Project Status

- ✅ **Core Module**: Complete (interface design, core implementations)
- 🔄 **Model Layer**: Repository(File, DB) (in progress); State, Event (mostly complete)
- 🔄 **ViewModel / View**: In progress (import path, naming, responsibility, pattern unification)
- 🔄 **Test/Docs/Automation**: In progress (CI, pytest, mypy, pdoc)

---

## Architecture

- **SOLID Principles**: SRP, OCP, LSP, ISP, DIP
- **Interface-based Design**: Protocols for clear contracts
- **Layered Architecture**: Core, Model, ViewModel, Platforms, View

## Architecture Diagram

![Architecture Diagram](src/images/architecture_01_EN.png)

### Layer Overview

- **core**: Core business logic, interfaces, and implementations
- **model**: Business logic extension (repositories, services, state, events)
- **viewmodel**: ViewModel layer (state transformation, UI logic)
- **platforms**: Cross-platform adapters (between viewmodel and view, Adapter pattern)
- **view**: View layer (PyQt6/QML UI components)

<details>
<summary>Project Structure</summary>

```text
├── core/                     # Core business logic
│   ├── interfaces/           # Core interfaces (tree, item, data, types, utils, keys)
│   └── impl/                 # Core implementations (tree, item, types, utils)
│   └── exceptions.py         # Core exceptions
├── model/                    # Business logic extension layer
│   ├── store/                # Data persistence (repo, file, db)
│   ├── state/                # State management
│   ├── action/               # Action handling
│   ├── traversal/            # Tree traversal logic
│   └── events/               # Event handling
├── viewmodel/                # ViewModel layer
│   ├── interfaces/           # ViewModel interfaces
│   └── impl/                 # ViewModel implementations
│       ├── tree_viewmodel_core.py    # Core logic for ViewModel
│       ├── tree_viewmodel_model.py   # Model-related ViewModel logic
│       ├── tree_viewmodel_view.py    # View-related ViewModel logic
│       └── tree_viewmodel.py         # Main ViewModel class
├── view/                     # View/UI layer
├── platforms/                # Platform-specific code (adapters, interfaces)
├── debug/                    # Debugging tools and viewers
├── tests/                    # Test code (pytest)
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
```

</details>

---

## Tech Stack

- **Backend**: Python 3.10
- **Frontend**: PyQt6
- **Data Management**: SQLite, File-based storage
- **Architecture**: MVVM pattern, Protocol-based interfaces

---

## Design Principles & Patterns

- **Protocol-based Interfaces**: Structural typing and static type checking (mypy) for flexible, reliable contracts.
- **MVVM Architecture**: Clear separation of UI and business logic, enabling independent ViewModel testing and maintainable code.
- **Dependency Inversion**: Core logic depends on abstractions, not implementations, for extensibility and modularity.
- **Observer Pattern**: Decoupled state change notifications (subscribe/notify, Qt signal/slot) for reactive UI updates.
- **Repository Pattern**: Abstracted data access layer for easy backend switching (DB, file, etc.).
- **State Pattern (Undo/Redo)**: StateManager encapsulates state transitions and history, simplifying ViewModel logic.

---

## Development Standards & Quality Assurance

- **Coding Style**: Follows the rules defined in `CODING_STYLE.md`.
- **Static Type Checking**: Ensures type safety across the codebase using `mypy`.
- **Unit Testing**: Automated testing with `pytest` (test coverage is being expanded).
- **Linting & Import Sorting**: Uses `flake8` for linting and `isort` for import sorting (configured in `setup.cfg`).
- **Continuous Integration**: Automated build, test, and type checking on every PR/commit via GitHub Actions or similar CI tools.

---

## Installation & Usage

1. **Python 3.10 or higher** is required.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Set up PostgreSQL if using DB persistence.
4. Run the application:
   ```bash
   python main.py
   ```
5. For packaged executable (Windows):
   - Build with PyInstaller:
     ```bash
     pyinstaller main.py --onefile --windowed --paths=src --add-data "src/images/icons;src/images/icons"
     ```
   - The executable will be in the `dist/` folder.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
