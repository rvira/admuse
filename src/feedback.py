# src/feedback.py
import chromadb
from config import CHROMA_PATH

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="liked_ads")
edits_collection = client.get_or_create_collection(name="ad_edits")


def save_edit(idea: str, generated: str, edited: str):
    """Record one draft->edit pair so future generations can learn the marketer's style.

    Only call this when `edited` actually differs from `generated` — an unchanged
    draft teaches nothing.
    """
    new_id = f"edit_{edits_collection.count()}"
    edits_collection.add(
        ids=[new_id],
        documents=[idea],  # Embedded for similarity search.
        metadatas=[{"generated": generated, "edited": edited}],
    )


def get_relevant_edits(idea: str, how_many: int = 3):
    """Return [(generated, edited), ...] for past edits most similar in meaning to `idea`."""
    if edits_collection.count() == 0:
        return []
    results = edits_collection.query(
        query_texts=[idea],
        n_results=min(how_many, edits_collection.count()),
    )
    metas = results["metadatas"][0]
    return [(m["generated"], m["edited"]) for m in metas]


def format_learned_examples(idea: str, how_many: int = 3) -> str:
    """Build a few-shot block (or "" if none) to inject into the copy prompt.

    The empty-string default matters: the prompt templates always expect a
    {learned_examples} value, so a cold start simply contributes nothing.
    """
    pairs = get_relevant_edits(idea, how_many)
    if not pairs:
        return ""
    lines = [
        "\n\nThis brand's marketers have edited past AI drafts as shown below. "
        "Study how they sharpened tone, length, and word choice, and write in that "
        "preferred style:",
    ]
    for generated, edited in pairs:
        lines.append(
            f"- AI draft: {generated}\n  Marketer's preferred version: {edited}"
        )
    return "\n".join(lines)


def save_liked_ad(idea: str, ad_copy: str):
    """Store an ad the user liked, so we can recall similar ones later."""
    # A unique id per entry. Using the current count is a simple beginner-friendly id.
    new_id = f"ad_{collection.count()}"

    collection.add(
        ids=[new_id],
        documents=[ad_copy],  # The text that gets embedded + searched.
        metadatas=[{"idea": idea}],  # Extra info stored alongside it.
    )


def find_similar_ads(idea: str, how_many: int = 3):
    """Given a new idea, find past liked ads with similar meaning."""
    if collection.count() == 0:
        return []  # Nothing saved yet.

    results = collection.query(
        query_texts=[idea],  # Chroma embeds this and compares by meaning.
        n_results=min(how_many, collection.count()),
    )
    # results["documents"] is a list-of-lists (one inner list per query). We sent one query.
    return results["documents"][0]
