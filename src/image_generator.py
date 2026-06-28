# src/image_generator.py
from huggingface_hub import InferenceClient
from config import HF_TOKEN, IMAGE_MODEL

client = InferenceClient(token=HF_TOKEN)


def generate_image(image_prompt: str, save_path: str = "generated_ad.png"):
    """Send a text prompt to Hugging Face and get back an image."""

    image = client.text_to_image(
        prompt=image_prompt,
        model=IMAGE_MODEL,
    )

    image.save(save_path)
    return save_path


if __name__ == "__main__":
    test_prompt = (
        "A sleek, trustworthy fintech scene: a person completing a video KYC "
        "verification on a smartphone, a glowing shield and checkmark hologram "
        "hovering above the screen, secure blue and teal tones, clean modern "
        "lighting, abstract data and network motifs in the background, "
        "professional and reassuring mood, photorealistic. No text in the image."
    )
    path = generate_image(test_prompt)
    print("Image saved to:", path)
