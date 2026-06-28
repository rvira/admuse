# Ad Generation Pipeline

A multi-modal ad generation pipeline. It pairs a **local LLM** (Ollama) for ad copy with a **cloud image model** (Hugging Face Inference API), wraps it in a **Streamlit** UI, and adds a **ChromaDB** memory loop that remembers ads you liked.

The default brand profile (`src/brand.py`) is pre-tuned to brand's voice and audience, so out of the box it writes copy for products like video KYC, document verification, liveness detection, and background checks. Edit the brand live in the sidebar to retune.

```
ad-generation-pipeline/
├── .env                 # Your secret HF token (NEVER commit). Create from .env.example.
├── .env.example         # Safe template of required keys.
├── .gitignore           # Ignores .env, venv, chroma_db/, caches.
├── requirements.txt     # Python dependencies.
├── config.py            # Loads settings + secrets from .env.
├── app.py               # The Streamlit UI — run this.
└── src/
    ├── __init__.py
    ├── brand.py             # brand profile: voice, audience, values.
    ├── prompts.py           # LangChain prompt templates.
    ├── text_generator.py    # Ollama → ad copy + image prompt.
    ├── image_generator.py   # Hugging Face → the actual image.
    └── feedback.py          # ChromaDB read/write for the memory loop.
```

## Quick start

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Local LLM
# Install Ollama from https://ollama.com, then:
ollama pull llama3

# Secrets
cp .env.example .env              # then paste your hf_... token into HF_TOKEN
```

## Test each piece (in order)

```bash
python -m src.text_generator      # prints ad copy → LLM works
python -m src.image_generator     # saves generated_ad.png → images work
streamlit run app.py              # opens the full UI
```

## Notes

- **Ollama** runs locally at `http://localhost:11434` — no API key, no per-request cost.
  If Python says "connection refused", run `ollama serve` and confirm the model name in
  `config.py` matches `ollama list` exactly (case-sensitive).
- **Hugging Face** is the only cloud piece. A free **Read** token works for prototyping.
  A `401` means the token is missing/wrong; never commit `.env`.
- **Image model fallbacks** — if `stabilityai/stable-diffusion-xl-base-1.0` 404s, switch
  `IMAGE_MODEL` in `config.py` to `black-forest-labs/FLUX.1-schnell` or
  `stabilityai/stable-diffusion-2-1`. Check a model's page for the "Inference Providers"
  widget to confirm it's callable.
- **ChromaDB** stores liked ads in `chroma_db/` (gitignored) and finds similar ones by meaning, not keywords.
