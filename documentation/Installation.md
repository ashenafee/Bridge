# Installation

This section describes how to install Bridge on your local machine.

## Prerequisites

Before installing Bridge, make sure you have the following prerequisites:

- Python 3.11

## Step 1: Clone the Repository

First, clone the repository to your local machine:

```sh
git clone https://github.com/ashenafee/Bridge.git
```

## Step 2: Create a Virtual Environment

To install any dependencies needed by Bridge, we need to setup a virtual environment:

```sh
python -m venv venv
```

## Step 3: Activate the Virtual Environment

Next, activate the virtual environment:

### Windows
```sh
venv\Scripts\activate.bat
```

### UNIX-based Systems (macOS, Linux, etc.)
```sh
source venv/bin/activate
```

## Step 4: Install Dependencies

Once the environment is set up, we need to install the dependencies:

```sh
pip install -r requirements.txt
```

## Step 5: Run the Application

Finally, run the application:

```sh
python bridge.py
```

On your first run, you will be prompted to enter your NCBI email and API key. You can follow instructions on how to achieve this [here](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/). Once that's setup, subsequent runs will not prompt you for this information.