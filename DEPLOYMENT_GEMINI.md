# BD Tools — Gemini + Streamlit deployment

## 1. Create a Gemini API key

1. Open Google AI Studio: https://aistudio.google.com/apikey
2. Sign in with your Google account.
3. Click **Create API key**.
4. Create/select a Google AI Studio project.
5. Copy the key and keep it private.

The app is configured for `gemini-3.8-flash` by default.

## 2. Upload this project to GitHub

Upload the **contents of `BD-main`** to the root of your GitHub repository. At the repository root you should see:

- `main.py`
- `gemini_client.py`
- `requirements.txt`
- `style.css`
- `logo.png`
- `CVs_REFs_adapter/`
- `CVs_adapter/`
- `REF_creater/`

Do **not** upload a real `.streamlit/secrets.toml` file. The repository includes `.gitignore` to protect it.

## 3. Deploy on Streamlit Community Cloud

1. Open https://share.streamlit.io/
2. Sign in with GitHub.
3. Click **Create app**.
4. Select your GitHub repository.
5. Branch: `main`
6. Main file path: `main.py`
7. Open **Advanced settings**.
8. In **Secrets**, paste:

```toml
[gemini]
api_key = "PASTE_YOUR_GEMINI_API_KEY_HERE"
model = "gemini-3.8-flash"
```

9. Save the settings.
10. Click **Deploy**.

## 4. If the app is already deployed

Open the app → **Manage app** → **Settings** → **Secrets** and replace the old OpenAI secret with the Gemini block above, then save/reboot the app.

## Security

Never put the real API key in GitHub, `main.py`, or another Python file. The key belongs only in Streamlit Secrets (or a local `.streamlit/secrets.toml` that is not committed).
