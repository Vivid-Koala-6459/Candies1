# Candies Coffee & Food Ordering Prototype

## Run on Windows

1. Install Python 3.11+.
2. Open Command Prompt in this folder.
3. Run:

```text
pip install -r requirements.txt
streamlit run app.py
```

The browser should open automatically.

## Configure the shop

- `config/menu.json` — products, descriptions, prices and image filenames.
- `config/settings.json` — milk, sizes, add-ons, pickup interval, capacity and opening hours.
- Put product images in `images/coffee/` and `images/food/`, then set the corresponding image filename in `menu.json`.

## Payments

The prototype deliberately does not process real payments. The checkout includes Apple Pay / Google Pay / Card as UX placeholders. For production, connect Stripe Payment Element / Checkout and enable Apple Pay and Google Pay after the merchant/domain requirements are completed.
