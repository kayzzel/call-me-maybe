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
  ```make run FUNCTIONS=<file> INPUT=<file> OUTPUT=<file> OTHER=<other flag(s)/info>```<br>

  + Run the program in debug mode:<br>
  ```make debug```<br>
  
</details>

<details>
  <summary><h4>Usage Example</h4></summary>

  ```make run FUNCTIONS=example_func.json INPUT=example_input.json```<br><br>
  ```
example_func.json

[
  {
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": {
      "a": {
        "type": "number"
      },
      "b": {
        "type": "number"
      }
    },
    "returns": {
      "type": "number"
    }
  },
  {
    "name": "fn_greet",
    "description": "Generate a greeting message for a person by name.",
    "parameters": {
      "name": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  }
]
  ```
  ```
example_input.json

[
  {
    "prompt": "What is the sum of 2 and 3?"
  },
  {
    "prompt": "What is the sum of 265 and 345?"
  },
  {
    "prompt": "Greet shrek"
  },
  {
    "prompt": "Greet john"
  }
]
  ```

</details>

<details>
  <summary><h4>Resources</h4></summary>

  ___
  ### 1. Links:
  - [PyQt6 tuto](https://www.pythonguis.com/pyqt6-tutorial/)<br>

  
  ### 2. AI Usage:
  Claud and gemini were used a little bit, mostly for some explanations on how use PyQt6. And for some debuging<br><br>
</details>
