# PolaRiS Bench Real World Evals

## Installation
Install UV following [this link](https://docs.astral.sh/uv/getting-started/installation/) if not already installed

```bash
uv sync
```

Install ZED Python API (assuming you already have ZED SDK installed on your system, which you should for DROID)
```bash
source .venv/bin/activate
python /usr/local/zed/get_python_api.py
# This will install a pyzed wheel in your local directory, install it to your venv
uv pip install ./path-to-pyzed.wh
```

Copy your DROID parameters file to this repo
```bash
cp /path/to/your/parameters.py ./droid/misc/parameters.py
```

## Configure Tasks
In the `evals` folder, create a JSON for your task like below. Specify the progress criteria like below (ideally these can be implemented in simulation). Try to use the naming convention: `Institution-Task-#`. Try to keep tasks mostly rigid-body and simulatable.

`evals/uw-task-1.json`
```json
{
    "instruction": "stack the cubes on the green tray",
    "criteria": [
        "One block on tray",
        "Second block on tray",
        "Both blocks stacked on each other on tray"
    ]
}
```


## Running Evals
TODO: make table for policies available

TODO: eval script which
- Stores all trajectory (frames, proprioception, camera extrinsics...) using DROID trajectory writer
    - modified to save raw frames instead of compression to haev 1:1 comparison for video model eval
- Success/progress labels
- Restoring initial conditions?