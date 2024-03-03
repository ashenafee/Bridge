# Bridge: Batch Coding Sequence Downloader

This documentation will guide you through setting up the backend and frontend for the graphical user interface (GUI) for downloading batch coding sequences.

## Prerequisites

- [Node.js](https://nodejs.org/en/download/)
- [Python 3.11+](https://www.python.org/downloads/)
- NCBI Entrez API key

## NCBI Configuration

### Obtaining an NCBI Entrez API Key

1. Sign in to your NCBI account or create a new one [here](https://www.ncbi.nlm.nih.gov/account/).

2. After signing in, navigate to your account's [settings](https://account.ncbi.nlm.nih.gov/settings/) page.

3. Scroll to the section titled **API Key Management** and click the **Create an API Key** button.

For more information, refer to [this](https://support.nlm.nih.gov/knowledgebase/article/KA-05317/en-us) guide by the NCBI.

### Setting the NCBI Entrez API Key

1. Navigate to the root directory of the repository.

2. Create a new file named `.env`.

3. Open the `.env` file in a text editor and add the following line.

    ```env
    NCBI_API_KEY=your_api_key
    ```

## App Setup

Make sure to do the setup for backend and frontend in different terminal windows.

### Backend

1. Navigate to the `backend` directory.

```bash
cd backend
```

2. Create a virtual environment.

```bash
python -m venv venv
```

3. Activate the virtual environment.

**UNIX/macOS**
```bash
source venv/bin/activate
```

**Windows**
```bash
venv\Scripts\activate
```

4. Install the required packages.

```bash
pip install -r requirements.txt
```

5. Run the backend server.

```bash
uvicorn main:app --reload
```

### Frontend

1. Navigate to the `frontend` directory.

```bash
cd frontend
```

2. Install the required packages.

```bash
npm install
```

3. Run the frontend server.

```bash
npm run dev
```

## Usage

1. Open your web browser and navigate to `http://localhost:5173`.

2. Enter the taxonomy name in the first input box.

3. Enter the gene symbol in the second input box.

4. Click the `Download` button.

## FAQs

**I've clicked the `Download` button, but the console shows an error. What should I do?**

This is a known issue. To get past it, click the `Download` button again.