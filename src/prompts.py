# src/prompts.py
from langchain_core.prompts import ChatPromptTemplate

# This template tells the LLM HOW to behave and WHAT to produce.
# The pieces in {curly_braces} are placeholders filled in at runtime.
AD_COPY_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert advertising copywriter for the brand '{brand_name}'. "
     "The brand operates in {industry}. "
     "Its voice is {voice}. Its core values are {values}. "
     "The target audience is {audience}. "
     "Never use these words: {forbidden_words}."
     "{learned_examples}"),
    ("human",
     "Write a short, punchy ad for this product or idea: {product_idea}.\n"
     "Return ONLY the ad copy: a headline plus 1-2 sentences. No preamble."),
])

# Campaign template: one idea -> several DISTINCT variants in a parseable format.
# We ask for a strict "VARIANT n / Headline: / Body:" layout because local LLMs are
# more reliable at fixed text shapes than at valid JSON.
CAMPAIGN_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert advertising copywriter for the brand '{brand_name}'. "
     "The brand operates in {industry}. "
     "Its voice is {voice}. Its core values are {values}. "
     "The target audience is {audience}. "
     "Never use these words: {forbidden_words}."
     "{learned_examples}"),
    ("human",
     "Create {num_variants} DISTINCT ad variants for this product or idea: {product_idea}.\n"
     "Make the variants genuinely different in angle (e.g. benefit-led, problem-led, "
     "social-proof, urgency) so a marketer can A/B test them.\n"
     "Return ONLY the variants, each in EXACTLY this format and nothing else:\n\n"
     "VARIANT 1\n"
     "Headline: <one punchy line>\n"
     "Body: <1-2 sentences>\n\n"
     "VARIANT 2\n"
     "Headline: ...\n"
     "Body: ...\n"),
])

# Visual-style presets. Each label maps to a descriptor string injected into the
# image prompt so the art direction (characters AND objects) renders in that style.
# Add or tweak entries freely — the UI builds its dropdown from these keys.
STYLE_PRESETS = {
    "Photorealistic": "photorealistic, professional product photography, realistic lighting, natural depth of field, high detail",
    "Comic book": "bold comic-book illustration: thick black ink outlines, halftone dot shading, vibrant saturated flat colors, dynamic cel-shaded characters and objects, expressive poses, graphic-novel art style",
    "3D render": "polished 3D render, soft studio lighting, smooth clean CGI surfaces, subtle reflections, octane-style render",
    "Flat vector": "modern flat vector illustration, clean geometric shapes, bold simple color palette, minimal corporate-memphis style",
    "Watercolor": "soft watercolor painting, organic brush textures, gentle color washes, hand-painted feel",
}
DEFAULT_STYLE = "Photorealistic"

# A SECOND template that turns the ad concept into a visual description
# we can later hand to the image model.
IMAGE_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system",
     "You are an art director. You convert ad concepts into vivid, concrete "
     "image-generation prompts for a text-to-image AI. The image must clearly "
     "depict the specific product or scenario being advertised — use literal "
     "subjects and concrete visual metaphors that make the offering obvious at a "
     "glance, never a generic office or workspace stand-in."),
    ("human",
     "The brand is '{brand_name}' ({industry}), with a {voice} voice.\n"
     "The product/idea being advertised is: '{product_idea}'.\n"
     "The ad copy is: '{ad_copy}'.\n"
     "Render every character and object in this VISUAL STYLE: {visual_style}.\n"
     "Write a single detailed image prompt (one paragraph) for this specific "
     "product/idea. Center the scene on a concrete depiction of '{product_idea}' "
     "(show the actual subject and relevant visual metaphors — e.g. documents, "
     "devices, shields, magnifiers, charts, flagged anomalies — as fits the idea), "
     "rendered consistently in the visual style above, then describe lighting and "
     "mood that suit both that style and the brand voice. "
     "Do not include any text, words, letters, or numbers in the image. "
     "Return ONLY the prompt, with no preamble."),
])
