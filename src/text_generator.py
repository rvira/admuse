# src/text_generator.py
import re

from langchain_ollama import ChatOllama
from config import OLLAMA_MODEL, OLLAMA_BASE_URL
from src.prompts import AD_COPY_TEMPLATE, IMAGE_PROMPT_TEMPLATE, CAMPAIGN_TEMPLATE

# Create one LLM connection we can reuse.
llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.7,
)


def generate_ad_copy(brand: dict, product_idea: str, learned_examples: str = "") -> str:
    """Fill the ad-copy template with brand data, send it to Ollama, return the text.

    learned_examples is an optional few-shot block (built by feedback.format_learned_examples)
    that nudges the copy toward styles this brand's marketers previously preferred.
    """

    chain = AD_COPY_TEMPLATE | llm

    response = chain.invoke(
        {
            "brand_name": brand["name"],
            "industry": brand["industry"],
            "voice": brand["voice"],
            "values": brand["values"],
            "audience": brand["audience"],
            "forbidden_words": brand["forbidden_words"],
            "product_idea": product_idea,
            "learned_examples": learned_examples,
        }
    )

    return response.content.strip()


def _parse_variants(raw: str) -> list[dict]:
    """Parse the 'VARIANT n / Headline: / Body:' layout into a list of dicts.

    Lenient on purpose: local LLMs occasionally wander from the format, so we extract
    whatever Headline/Body pairs we can find rather than failing the whole campaign.
    """
    variants = []
    # Split on 'VARIANT <n>' markers; the first chunk before VARIANT 1 is preamble.
    chunks = re.split(r"(?im)^\s*variant\s*\d+\s*$", raw)
    for chunk in chunks:
        headline = re.search(r"(?im)^\s*headline\s*:\s*(.+)$", chunk)
        body = re.search(
            r"(?im)^\s*body\s*:\s*(.+(?:\n(?!\s*headline\s*:).*)*)$", chunk
        )
        if headline:
            variants.append(
                {
                    "headline": headline.group(1).strip(),
                    "body": body.group(1).strip() if body else "",
                }
            )
    return variants


def generate_campaign(
    brand: dict, product_idea: str, num_variants: int = 3, learned_examples: str = ""
) -> list[dict]:
    """Generate several distinct ad variants for one idea.

    Returns a list of {"headline": str, "body": str}. If parsing comes up short
    (model ignored the format), falls back to single-ad generation so the UI still works.
    """
    chain = CAMPAIGN_TEMPLATE | llm
    response = chain.invoke(
        {
            "brand_name": brand["name"],
            "industry": brand["industry"],
            "voice": brand["voice"],
            "values": brand["values"],
            "audience": brand["audience"],
            "forbidden_words": brand["forbidden_words"],
            "product_idea": product_idea,
            "num_variants": num_variants,
            "learned_examples": learned_examples,
        }
    )
    variants = _parse_variants(response.content)

    if not variants:
        # Graceful fallback: treat the whole reply as one variant.
        copy = response.content.strip()
        variants = [{"headline": copy.split("\n", 1)[0].strip(), "body": copy}]
    return variants[:num_variants]


def generate_image_prompt(
    brand: dict, ad_copy: str, product_idea: str, visual_style: str = ""
) -> str:
    """Turn finished ad copy into a visual prompt for the image model. product_idea is passed through so the image stays anchored to the concrete subject instead of drifting into generic office/workspace imagery.visual_style is an art-style descriptor (e.g. the "Comic book" preset from prompts.STYLE_PRESETS). It is woven into the prompt AND appended verbatim at the end, because text-to-image models weight an explicit trailing style tag heavily and the local LLM sometimes softens stylistic instructions."""
    # Default keeps prior behaviour for callers that don't pass a style.
    style = visual_style.strip() or "photorealistic, professional, realistic lighting"

    chain = IMAGE_PROMPT_TEMPLATE | llm
    response = chain.invoke(
        {
            "brand_name": brand["name"],
            "industry": brand["industry"],
            "voice": brand["voice"],
            "ad_copy": ad_copy,
            "product_idea": product_idea,
            "visual_style": style,
        }
    )
    prompt = response.content.strip()
    return f"{prompt} Overall art style: {style}."


if __name__ == "__main__":
    from src.brand import DEFAULT_BRAND

    idea = "an AI-powered video KYC solution that verifies a customer's identity in under 30 seconds"
    copy = generate_ad_copy(DEFAULT_BRAND, idea)
    print("--- AD COPY ---\n", copy)
    img_prompt = generate_image_prompt(DEFAULT_BRAND, copy, idea)
    print("\n--- IMAGE PROMPT ---\n", img_prompt)

    print("\n--- CAMPAIGN (3 variants) ---")
    for i, v in enumerate(generate_campaign(DEFAULT_BRAND, idea, num_variants=3), 1):
        print(f"\nVariant {i}\n  Headline: {v['headline']}\n  Body: {v['body']}")
