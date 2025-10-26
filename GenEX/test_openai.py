from openai import OpenAI

# Crée le client avec ta clé
client = OpenAI(api_key="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")

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Bonjour"}],
        max_tokens=10
    )
    print(response.choices[0].message.content)

except Exception as e:  # Capture toutes les erreurs OpenAI
    print("Erreur OpenAI :", e)
