
## Team

| Name | Study program | Email |
|------|---------------|-------|
| Yashwanth Chithaloori | Masters in Artificial Intelligence | yashwanthgoud.chithaloori@study.thws.de |
| Sai Surya | Masters in Artificial Intelligence | saisurya.mada@study.thws.de |
| Aliesha Antoni | Bachelor Cybersecurity | alieshaantoni@gmail.com |
| Eva Weber | Cybersecurity | evatigweb@gmail.com |
| Öykü Akay | Cybersecurity | oyku.akay06@gmail.com |
| Meera Elizabeth Stephen | Computer Science | meera.elizabeth.s@gmail.com |
| Anita Oppelt            | Soziale Arbeit    | Anita.Oppelt@study.thws.de |

# MAUS-Assistent

A small web app that helps workshop staff fill out the **MAUS assessment form** (Erhebungsbogen A) for a participant, and then creates an **Eingliederungsplan** (integration plan) as a PDF.

Instead of filling in a long form by hand, the staff member just chats with an AI assistant about the participant. The assistant suggests scores for each trait and writes the plan.

## What it does

1. **Chat interview** – the AI asks questions about the participant (how they behave in a group, how they work, etc.).
2. **Scores for all MAUS traits (A–F)** – social skills, method skills, personal skills, work skills, and more. The app only allows scores that are valid on the real form.
3. **Looks up your own data (RAG)** – it searches the participant's earlier DOKU notes and the DIK-2 catalogue, so suggestions are based on real records, not just guesses.
4. **PDF export** – creates the Eingliederungsplan as a PDF you can download.
5. **Privacy** – real names and birthdates are replaced with a pseudonym (e.g. `Klient_27236`) before anything is sent to the AI.

## How to run it

You need Python 3.10 or newer.

```bash
# 1. Install the packages
pip install -r requirements.txt

# 2. Create your settings file
copy .env.example .env        # Windows
# cp .env.example .env        # Mac / Linux

# 3. Open .env and put your API key in (see "Choosing an AI provider" below)

# 4. Start the app
streamlit run app.py
```

The app opens in your browser. Pick a participant, then chat.

## Choosing an AI provider

Set `LLM_PROVIDER` in `.env`:

| Value | What it uses | Key to set |
|-------|--------------|------------|
| `gemini` | Google Gemini | `GEMINI_API_KEY` |
| empty | Any OpenAI-compatible service (Groq, xAI, ...) | `LLM_API_KEY`, `LLM_BASE_URL` |

Optional: set `LLM_FALLBACK_MODEL` to use a second model if the main one is overloaded.

## Using your own data

Put the workshop Excel exports in a folder called `data/`:

- DOKU-Bogen (documentation sheets)
- Anwesenheit (attendance)
- Klienten (participant master data)

If `data/` does not exist, the app automatically uses the **fake example data** in `sample_data/`, so you can try it out right away.

> **Important:** `data/` is ignored by git on purpose. Never commit real participant data.

To regenerate the fake example data: `python make_sample_data.py`

## Project files

| File | What it's for |
|------|---------------|
| `app.py` | The web app (screens, chat, buttons) |
| `llm.py` | Talks to the AI provider |
| `maus.py` | The MAUS traits, allowed score ranges, DIK-2 lookup |
| `rag.py` | Searches the DOKU notes and DIK-2 text for relevant information |
| `data.py` | Loads the Excel files |
| `privacy.py` | Replaces names and dates before sending text to the AI |
| `eingliederungsplan_pdf.py`, `pdf_out.py` | Create the PDF files |
| `build_dik.py` | One-time script that turns the DIK-2 PDF into `dik2.json` |
| `make_sample_data.py` | Creates the fake example data |
| `.env.example` | Template for your settings |


