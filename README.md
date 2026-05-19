*This project has been created as part of the 42 curriculum by gabach.*

# ---- CALL-ME-MAYBE ----

<details>
  <summary><h4>Description</h4></summary>

  ___

  + General description: <br>
 
</details>
<details>
  <summary><h4>Instructions</h4></summary>

  ___
  ### 1. Makefile
  + Install dependencies and run the program:<br>
  ```make```<br>

  + Install dependencies: <br>
  ```make install```<br>

  + Clean temporary files and caches: <br>
  ```make clean```<br>

  + Check flake8 and mypy norms, also have a stricter rule: <br>
  ```make lint```<br>
  ```make lint-strict```<br>

  + For other command there is a help: <br>
  ```make help```

  ### 2. Execution
  
  + Install the package Run the program (with default files name): <br>
  ```make```<br>
  
  + Run the program (with default files name): <br>
  ```make run```<br>

  + Run the program with custom files:<br>
  ```make run FUNCTIONS=<file> INPUT=<file> OUTPUT=<file>```<br>

  + Run the program in debug mode:<br>
  ```make debug```<br>
  
</details>

<details>
  <summary><h4>Algorithm</summary>

___
## Core Strategy

**Sequential Pathfinding:** Find path for each drone one at a time, maintaining a shared reservation table to prevent capacity conflicts.

## Key Components

### 1. ExploringDrone (Search State)
- `path`: Hubs visited (`None` = in-transit to restricted zone)
- `connections`: Connections taken
- `actual_hub`: Current location
- `in_transit_to_restricted`: Flag for 2-turn restricted zone movement

### 2. Turn (Reservation Table)
Tracks per-turn resource usage:
- `moves`: Connections used this turn
- `hubs`: Drone occupancy per hub `{name, drones_in, max_drones}`

Prevents capacity violations across all drones.

### FOR each drone:

##### 1. Initialize exploring_drone at start_hub
##### 2. WHILE not at end_hub:

  - Try all connections from current positions
  - Check reservations (capacity constraints)
  - Generate new states for valid moves
  - Keep drones that wait (capacity blocked)
  - Deduplicate: keep shortest path per hub


##### 3. Select first drone reaching end_hub
##### 4. Record path in reservation tables

## Special Cases

**Restricted Zones (2 turns):**
- Turn 1: Commit to move, stay at origin, mark in-transit
- Turn 2: MUST complete or fail (no waiting on connection)

**Waiting:** Drones stay at current hub when blocked, path appends `None`

**Cycle Prevention:** No revisiting hubs (`if next_hub in path: reject`)

**Deduplication:** Keep only shortest path per hub location

## Complexity

- **Time:** O(N × T × H × C) - N drones, T turns, H hubs, C connections/hub
- **Space:** O(T × H) - Turn tables + O(H) active exploring drones
- **Optimization:** Deduplication limits exploring drones to O(H) per tur

</details>

<details>
  <summary><h4>Visual representation</summary>
    
___
#### **Core Features**

* **Adaptive Map Engine:**
    * A custom-rendered canvas using `QPainter`
    * **Intuitive Navigation:** support for **mouse-wheel zooming** and **click-and-drag panning**, allowing for exploration of hub networks.
* **Dynamic Hub Symbology:**
    * Visual differentiation of zone types through different geometries: **Circles** (Normal), **Triangles** (Priority), and **Squares** (Restricted) and **Cross** (Blocked).
    * Supports custom color-coding and "Rainbow" status indicators for specialized map nodes.
* **Playback & Temporal Control:**
    * A control bar featuring **Play/Pause**, **Step-by-Step** navigation, and **Instant Restart**.
    * Automated simulation timer with adjustable intervals for real-time monitoring.
    * A map switcher to easyli test different maps
* **Advanced Drone Tracking:**
    * **Path Trails:** Persistent dashed "snail trails" that visualize each drone's historical trajectory.
    * **Transit Logic:** Explicit visual rendering of drones in "mid-point" states when entering restricted 2-turn zones.
* **Live Telemetry Dashboard:**
    * A dynamic info panel providing text-based summaries of drone coordinates, fleet status, and active transit operations.

---

#### **Technical Implementation**

| Component | Responsibility |
| :--- | :--- |
| **`MapWidget`** | Handles coordinate scaling, zoom mathematics, and primitive shape rendering. |
| **`PannableScrollArea`** | Manages the "infinite canvas" interaction logic and mouse event overrides. |
| **`PlayerToolBar`** | Controls the simulation state machine and playback signals. |
| **`MainWindow`** | Orchestrates data flow between the pathfinding algorithm and the UI. |

</details>

<details>
  <summary><h4>Resources</h4></summary>

  ___
  ### 1. Links:
  - [PyQt6 tuto](https://www.pythonguis.com/pyqt6-tutorial/)<br>

  
  ### 2. AI Usage:
  Claud and gemini were used a little bit, mostly for some explanations on how use PyQt6. And for some debuging<br><br>
</details>
