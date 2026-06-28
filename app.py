# app.py
import streamlit as st

from src.brand import DEFAULT_BRAND
from src.prompts import STYLE_PRESETS, DEFAULT_STYLE
from src.text_generator import generate_campaign, generate_image_prompt
from src.image_generator import generate_image
from src.feedback import (
    save_liked_ad,
    find_similar_ads,
    save_edit,
    format_learned_examples,
)

st.set_page_config(page_title="Ad Generator", page_icon="🛡️")
st.title("🛡️ Multi-Modal Ad Generator")
st.caption(
    "Generate a full campaign of on-brand variants for brand's identity, KYC, and "
    "fraud-prevention products — then edit inline. The app learns from your edits."
)

# --- SIDEBAR: live brand editor + campaign size ---
# Whatever the user types here overrides the defaults, so they can retune the brand
# voice without touching code.
st.sidebar.header("Brand Profile")
brand = {
    "name": st.sidebar.text_input("Brand name", DEFAULT_BRAND["name"]),
    "industry": st.sidebar.text_input("Industry", DEFAULT_BRAND["industry"]),
    "voice": st.sidebar.text_area("Voice", DEFAULT_BRAND["voice"]),
    "audience": st.sidebar.text_area("Audience", DEFAULT_BRAND["audience"]),
    "values": st.sidebar.text_input("Values", DEFAULT_BRAND["values"]),
    "forbidden_words": st.sidebar.text_input(
        "Forbidden words", DEFAULT_BRAND["forbidden_words"]
    ),
}
st.sidebar.header("Campaign")
num_variants = st.sidebar.slider("How many variants?", 1, 5, 3)

st.sidebar.header("Image style")
style_label = st.sidebar.selectbox(
    "Visual style for generated images",
    list(STYLE_PRESETS),
    index=list(STYLE_PRESETS).index(DEFAULT_STYLE),
    help="Controls how characters and objects in the image are drawn — e.g. Comic book.",
)
style_descriptor = STYLE_PRESETS[style_label]

# --- MAIN AREA: the product idea + generate button ---
product_idea = st.text_input(
    "What are you advertising?",
    placeholder="e.g., an AI-powered video KYC solution that verifies identity in under 30 seconds",
)

# As the user types, surface past liked ads with a similar vibe.
if product_idea:
    similar = find_similar_ads(product_idea)
    if similar:
        with st.expander("💡 Past ads with a similar vibe"):
            for past_ad in similar:
                st.write("•", past_ad)

if st.button("Generate Campaign", type="primary"):
    if not product_idea:
        st.warning("Please describe what you're advertising first.")
    else:
        # Pull the most relevant past edits and feed them in as few-shot examples,
        # so each campaign drifts toward the styles marketers actually prefer.
        learned = format_learned_examples(product_idea)
        with st.spinner("Writing campaign variants with the local LLM..."):
            variants = generate_campaign(
                brand, product_idea, num_variants=num_variants, learned_examples=learned
            )

        # Stash so results + edits survive Streamlit's rerun on every click.
        st.session_state["variants"] = variants  # original AI drafts
        st.session_state["idea"] = product_idea
        st.session_state["images"] = {}  # index -> image path
        if learned:
            st.caption("✨ Applied lessons from your past edits.")

# --- Show + edit the campaign (persists across reruns via session_state) ---
variants = st.session_state.get("variants")
if variants:
    idea = st.session_state["idea"]
    st.subheader("Campaign variants")
    st.write(
        "Edit any variant inline — no regeneration needed. Then teach the app from your edits."
    )

    for i, v in enumerate(variants):
        with st.container(border=True):
            st.markdown(f"**Variant {i + 1}**")

            # Editable fields = live editing. Widget state holds the current edited text.
            edited_headline = st.text_input("Headline", v["headline"], key=f"hl_{i}")
            edited_body = st.text_area("Body", v["body"], key=f"body_{i}", height=100)

            col1, col2, col3 = st.columns(3)

            # 1) Teach from edits -> feeds the learning loop.
            with col1:
                if st.button("📚 Teach from my edits", key=f"teach_{i}"):
                    original = f"{v['headline']}\n{v['body']}".strip()
                    edited = f"{edited_headline}\n{edited_body}".strip()
                    if edited and edited != original:
                        save_edit(idea, original, edited)
                        st.success("Learned! Future copy will lean this way.")
                    else:
                        st.info("No change detected — edit the copy first.")

            # 2) Save a winner -> recall-by-similarity memory.
            with col2:
                if st.button("👍 Save winner", key=f"save_{i}"):
                    save_liked_ad(idea, f"{edited_headline}\n{edited_body}".strip())
                    st.success("Saved to memory.")

            # 3) Generate an image for the (edited) copy of this variant.
            with col3:
                if st.button("🎨 Generate image", key=f"img_{i}"):
                    copy_for_image = f"{edited_headline}. {edited_body}".strip()
                    with st.spinner(f"Designing the visual prompt ({style_label})..."):
                        image_prompt = generate_image_prompt(
                            brand, copy_for_image, idea, visual_style=style_descriptor
                        )
                    with st.spinner("Generating the image (this can take a moment)..."):
                        path = generate_image(
                            image_prompt, save_path=f"generated_ad_{i}.png"
                        )
                    st.session_state["images"][i] = path

            # Show this variant's image if one was generated.
            if i in st.session_state.get("images", {}):
                st.image(st.session_state["images"][i])
