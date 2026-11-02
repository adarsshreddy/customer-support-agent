# Customer Support Assistant

A Streamlit chat app that answers known questions from `faqs.json` and uses
Gemini for questions the FAQ does not cover. It cannot access customer accounts
or order records.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set `GOOGLE_API_KEY` to a Google AI Studio
   API key. `GEMINI_API_KEY` is also accepted.
4. Start the app:

   ```powershell
   python -m streamlit run agent.py
   ```

The app can run without an API key, but it will only answer questions that
match the local FAQ.

## Deploy online

Deploy this repository as a Streamlit app with `agent.py` as the entry point.
Add `GOOGLE_API_KEY` in the hosting provider's secret settings; never commit
the key or a populated `.env` file. The model can be changed with the optional
`GEMINI_MODEL` setting.

## Tests

Run the FAQ matching tests with:

```powershell
python -m unittest discover -s tests -v
```
