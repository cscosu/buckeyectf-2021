# Jupiter

- TODO: Make detailed write-up

## Overview

- You can upload a jupyter notebook
- The server will run `jupyter trust <your_notebook>.ipynb`
- The admin bot will visit your notebook

## Solution

- Put reverse shell payload in cell and execute it with
  ```js
Jupyter.notebook.execute_cells([0])
  ```
