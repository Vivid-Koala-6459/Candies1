import json, uuid
from datetime import datetime, date, timedelta
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).parent
CONFIG = ROOT / "config"
IMG = ROOT / "images"

st.set_page_config(page_title="Candies | Coffee & Food", page_icon="☕", layout="centered", initial_sidebar_state="collapsed")

def load_json(name):
    with open(CONFIG/name, "r", encoding="utf-8") as f:
        return json.load(f)

menu = load_json("menu.json")
settings = load_json("settings.json")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root { --green:#173f35; --sage:#6f907d; --cream:#f7f4ea; --mint:#e7efe8; --brown:#754c35; }
html,body,[class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:var(--cream); }
.block-container { max-width:760px; padding:1rem 1rem 5rem; }
header[data-testid="stHeader"] { background:transparent; }
.hero { background:linear-gradient(135deg,#173f35,#315e4d); color:white; border-radius:28px; padding:30px 26px; margin:0 0 20px; }
.brand { font-family:'Playfair Display',serif; font-size:42px; line-height:1; }
.hero p { margin:10px 0 0; opacity:.88; font-size:15px; }
.badge { display:inline-block; background:#dcebdd; color:#173f35; padding:7px 12px; border-radius:999px; font-size:12px; font-weight:700; margin-top:18px; }
.section { font-family:'Playfair Display',serif; color:#173f35; font-size:28px; margin:25px 0 10px; }
.card { background:white; border-radius:20px; padding:14px; margin:9px 0; border:1px solid #e2e4db; box-shadow:0 2px 10px rgba(23,63,53,.05); }
.price { color:#173f35; font-weight:700; font-size:17px; }
.desc { color:#6d746e; font-size:13px; margin:3px 0 10px; }
.pill { background:#edf3ee; color:#315e4d; border-radius:999px; padding:4px 9px; font-size:11px; font-weight:600; }
.total { background:#173f35; color:white; border-radius:20px; padding:18px; font-size:21px; font-weight:700; }
.small { color:#6d746e; font-size:12px; }
div.stButton > button { border-radius:14px; font-weight:700; min-height:42px; }
div[data-testid="stExpander"] { border-radius:16px; border:1px solid #e2e4db; background:white; }
</style>
""", unsafe_allow_html=True)

if "cart" not in st.session_state: st.session_state.cart=[]
if "page" not in st.session_state: st.session_state.page="menu"
if "order_no" not in st.session_state: st.session_state.order_no=None

def money(v): return f"${v:,.2f}"

def add_item(product, category, options=None):
    options = options or {}
    item = {"id":str(uuid.uuid4()), "name":product["name"], "category":category,
            "base_price":product["price"], "price":product["price"], "options":options}
    item["price"] += options.get("milk_price",0)+options.get("size_price",0)+options.get("addon_price",0)
    st.session_state.cart.append(item)
    st.toast(f"{product['name']} added to your order")

def cart_total(): return sum(x["price"] for x in st.session_state.cart)

def header():
    st.markdown("""<div class="hero">
      <div class="brand">Candies</div>
      <p>Good coffee. Good food. Ready when you are.</p>
      <span class="badge">● PICKUP ORDERS</span>
    </div>""", unsafe_allow_html=True)
    c1,c2 = st.columns([3,1])
    with c1: st.caption(f"{len(st.session_state.cart)} item{'s' if len(st.session_state.cart)!=1 else ''} in your order")
    with c2:
        if st.button("🛒 Basket", use_container_width=True):
            st.session_state.page="basket"; st.rerun()

def product_card(p, category):
    st.markdown(f"""<div class="card"><div style="font-size:18px;font-weight:700;color:#173f35">{p['name']}</div>
    <div class="desc">{p['description']}</div><span class="price">{money(p['price'])}</span></div>""", unsafe_allow_html=True)
    if category=="coffee":
        with st.expander("Customise"):
            milk_names=[x["name"] for x in settings["milk_options"]]
            size_names=[x["name"] for x in settings["sizes"]]
            m=st.selectbox("Milk", milk_names, key=p["id"]+"_m")
            s=st.selectbox("Size", size_names, key=p["id"]+"_s")
            addon_names=["None"]+[x["name"] for x in settings["add_ons"]]
            a=st.selectbox("Add-on", addon_names, key=p["id"]+"_a")
            mp=next(x["price"] for x in settings["milk_options"] if x["name"]==m)
            sp=next(x["price"] for x in settings["sizes"] if x["name"]==s)
            ap=0 if a=="None" else next(x["price"] for x in settings["add_ons"] if x["name"]==a)
            if st.button(f"Add · {money(p['price']+mp+sp+ap)}", key=p["id"]+"_add", use_container_width=True):
                add_item(p,category,{"milk":m,"milk_price":mp,"size":s,"size_price":sp,"add_on":a,"addon_price":ap})
    else:
        if st.button(f"Add · {money(p['price'])}", key=p["id"]+"_add", use_container_width=True):
            add_item(p,category)

def menu_page():
    header()
    st.markdown('<div class="section">Coffee & Tea</div>', unsafe_allow_html=True)
    for p in menu["coffee"]: product_card(p,"coffee")
    st.markdown('<div class="section">Food</div>', unsafe_allow_html=True)
    for p in menu["food"]: product_card(p,"food")
    if st.session_state.cart:
        st.markdown("---")
        if st.button(f"View basket · {money(cart_total())}", type="primary", use_container_width=True):
            st.session_state.page="basket"; st.rerun()

def basket_page():
    header()
    st.markdown('<div class="section">Your basket</div>', unsafe_allow_html=True)
    if not st.session_state.cart:
        st.info("Your basket is empty.")
        if st.button("Browse menu", use_container_width=True): st.session_state.page="menu"; st.rerun()
        return
    for i,item in enumerate(st.session_state.cart):
        opts=", ".join(str(v) for k,v in item["options"].items() if not k.endswith("_price") and v not in ("None",None))
        c1,c2=st.columns([4,1])
        with c1:
            st.markdown(f"**{item['name']}**  \n<span class='small'>{opts or 'Food item'}</span>",unsafe_allow_html=True)
        with c2:
            st.markdown(f"**{money(item['price'])}**")
            if st.button("Remove",key=f"rm{i}"): st.session_state.cart.pop(i); st.rerun()
    st.markdown(f'<div class="total">Order total <span style="float:right">{money(cart_total())}</span></div>',unsafe_allow_html=True)
    st.write("")
    c1,c2=st.columns(2)
    with c1:
        if st.button("← Menu",use_container_width=True): st.session_state.page="menu"; st.rerun()
    with c2:
        if st.button("Continue →",type="primary",use_container_width=True): st.session_state.page="pickup"; st.rerun()

def pickup_page():
    header()
    st.markdown('<div class="section">When should we have it ready?</div>',unsafe_allow_html=True)
    today=date.today()
    pickup_date=st.date_input("Pickup date",value=today,min_value=today)
    day=pickup_date.strftime("%A")
    opening=settings["opening_hours"][day]
    st.caption(f"{day}: {opening[0]} – {opening[1]}")
    start=datetime.combine(pickup_date,datetime.strptime(opening[0],"%H:%M").time())
    end=datetime.combine(pickup_date,datetime.strptime(opening[1],"%H:%M").time())
    slots=[]
    t=start
    while t <= end-timedelta(minutes=settings["pickup_interval_minutes"]):
        slots.append(t.strftime("%H:%M")); t += timedelta(minutes=settings["pickup_interval_minutes"])
    chosen=st.selectbox("Pickup time",slots)
    st.info("Pickup slots are held for demonstration. A production version can enforce live capacity per slot.")
    name=st.text_input("Your name")
    phone=st.text_input("Mobile number")
    email=st.text_input("Email address")
    notes=st.text_area("Order notes (optional)",height=80)
    if st.button("Continue to payment →",type="primary",use_container_width=True):
        if not name or not phone or not email: st.error("Please enter your name, mobile number and email.")
        else:
            st.session_state.customer={"name":name,"phone":phone,"email":email,"notes":notes,
                                       "date":pickup_date.strftime("%d %b %Y"),"time":chosen}
            st.session_state.page="payment"; st.rerun()

def payment_page():
    header()
    st.markdown('<div class="section">Payment</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="card"><b>Pickup</b><br>{st.session_state.customer["date"]} at {st.session_state.customer["time"]}<br><br><b>Total</b><br><span class="price">{money(cart_total())}</span></div>',unsafe_allow_html=True)
    st.markdown("### Choose payment")
    method=st.radio("Payment method",["Apple Pay","Google Pay","Card"],horizontal=True,label_visibility="collapsed")
    st.caption("Prototype payment gateway — no money will be charged.")
    if method=="Apple Pay":
        st.markdown(" **Apple Pay**")
    elif method=="Google Pay":
        st.markdown("**G Pay**  Google Pay")
    else:
        st.text_input("Card number",placeholder="1234 5678 9012 3456")
        c1,c2=st.columns(2); c1.text_input("Expiry",placeholder="MM / YY"); c2.text_input("CVC",placeholder="123")
    if st.button(f"Pay {money(cart_total())} →",type="primary",use_container_width=True):
        st.session_state.order_no="CAN-"+str(uuid.uuid4())[:8].upper()
        st.session_state.page="confirmation"; st.rerun()

def confirmation_page():
    st.markdown("""<div class="hero" style="text-align:center">
      <div style="font-size:52px">✓</div><div class="brand">Thank you!</div>
      <p>Your Candies order is confirmed.</p></div>""",unsafe_allow_html=True)
    c=st.session_state.customer
    st.markdown(f"""<div class="card">
    <div style="font-size:12px;color:#6d746e">ORDER NUMBER</div><div style="font-size:24px;font-weight:700;color:#173f35">{st.session_state.order_no}</div>
    <hr><b>Pickup</b><br>{c["date"]} at {c["time"]}<br><br><b>For</b><br>{c["name"]}<br><br><b>Total</b><br>{money(cart_total())}
    </div>""",unsafe_allow_html=True)
    st.success("We've got your order. See you at Candies!")
    if st.button("Start a new order",type="primary",use_container_width=True):
        st.session_state.cart=[]; st.session_state.page="menu"; st.session_state.order_no=None; st.rerun()

if st.session_state.page=="menu": menu_page()
elif st.session_state.page=="basket": basket_page()
elif st.session_state.page=="pickup": pickup_page()
elif st.session_state.page=="payment": payment_page()
else: confirmation_page()

with st.sidebar:
    st.markdown("## Candies prototype")
    st.caption("Admin/configuration")
    st.write("Edit `config/menu.json` to change products, prices and descriptions.")
    st.write("Edit `config/settings.json` to change milk, sizes, add-ons, pickup intervals, capacity and opening hours.")
    st.divider()
    st.caption("Production payment note")
    st.write("Apple Pay / Google Pay require a payment provider such as Stripe and domain/payment verification. This prototype uses a safe test checkout.")
