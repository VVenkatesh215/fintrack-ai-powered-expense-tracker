# Ollama Setup Guide for FinBot

FinBot now uses **Ollama** to run AI models locally on your machine, replacing the Cohere API. This means:
- No API keys needed
- No rate limits or costs
- Complete privacy - data never leaves your machine
- Works offline

## Step 1: Install Ollama

### Windows
1. Download Ollama from: https://ollama.com/download
2. Run the installer
3. Ollama will start automatically in the system tray

### Verify Installation
Open PowerShell and run:
```powershell
ollama --version
```

## Step 2: Pull a Model

FinBot is configured to use `llama3.2` by default. Pull it with:

```powershell
ollama pull llama3.2
```

**Alternative models** (if llama3.2 is too large or slow):
- `llama3.2:1b` - Smallest, fastest (1.3GB)
- `llama2` - Good balance (3.8GB)
- `phi` - Microsoft's small model (1.6GB)
- `mistral` - High quality (4.1GB)

To use a different model, pull it:
```powershell
ollama pull llama3.2:1b
```

Then update `utils/finbot.py` line 32 to use your chosen model:
```python
response = ollama.chat(
    model='llama3.2:1b',  # Change this to your model
    messages=[...]
)
```

## Step 3: Test Ollama

Test that Ollama is working:
```powershell
ollama run llama3.2 "Hello, how are you?"
```

You should see a response from the model.

## Step 4: Run FinTrack

Start your Streamlit app:
```powershell
streamlit run Home.py
```

Go to the **Report** page and open **FinBot** in the sidebar. Ask a financial question!

## Troubleshooting

### "Ollama not available" error
- Make sure Ollama is running (check system tray on Windows)
- Verify the model is pulled: `ollama list`
- Restart Ollama: Close from system tray and restart

### Slow responses
- Try a smaller model like `llama3.2:1b` or `phi`
- Ollama uses GPU if available, otherwise CPU (slower)

### Model not found
Run: `ollama pull <model-name>` to download the model first

## Available Models

See all available models at: https://ollama.com/library

Popular choices for FinBot:
- **llama3.2:1b** - Fastest, smallest (recommended for laptops)
- **llama3.2** - Good quality, medium speed
- **mistral** - High quality responses
- **phi** - Microsoft's efficient model

## Fallback Behavior

If Ollama is unavailable or fails, FinBot will automatically fall back to a local summary based on your transaction data. You'll see a note in the response.
