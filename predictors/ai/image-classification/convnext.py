#
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "muna",
#     "rich",
#     "torchvision",
# ]
# ///

from muna import compile, Sandbox
from muna.beta import OnnxRuntimeInferenceMetadata
from PIL import Image
from torch import randn, argmax, softmax
from torchvision.models import convnext_base, ConvNeXt_Base_Weights
from torchvision.transforms.functional import center_crop, normalize, resize, to_tensor

weights = ConvNeXt_Base_Weights.DEFAULT
model = convnext_base(weights=weights).eval()

@compile(
    tag="@pytorch/convnext",
    description="Image classification entirely using standard ConvNet modules.",
    access="public",
    sandbox=Sandbox().pip_install("torchvision", index_url="https://download.pytorch.org/whl/cpu"),
    metadata=[
        OnnxRuntimeInferenceMetadata(
            model=model,
            model_args=[randn(1, 3, 224, 224)]
        )
    ]
)
def classify_image(image: Image.Image) -> tuple[str, float]:
    """
    Classify an image using ConvNeXt (Base Model)

    Parameters:
        image (PIL.Image): Input image.

    Returns:
        str: Best guess at classification of image.
        float: Confidence in the classification.
    """
    # Preprocess image
    image = image.convert("RGB")
    image = resize(image, 232)
    image = center_crop(image, 224)
    image_tensor = to_tensor(image)
    normalized_tensor = normalize(
        image_tensor,
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
    # Run model
    logits = model(normalized_tensor[None])
    scores = softmax(logits, dim=1)
    idx = argmax(scores, dim=1)
    score = scores[0,idx].item()
    label = weights.meta["categories"][idx]
    # Return
    return label, score

if __name__ == "__main__":
    image = Image.open(f"media/cat.jpg")
    what, score = classify_image(image)
    print(what, score)