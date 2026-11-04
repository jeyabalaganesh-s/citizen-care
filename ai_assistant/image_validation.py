
import base64
from openai import OpenAI
from django.conf import settings



import json

from openai import OpenAI
from django.conf import settings


def validate_complaint_image(image_url, complaint_description):

    if not settings.OPENAI_API_KEY:
        raise ValueError("OpenAI API key is missing.")

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY
    )

    system_prompt = """
    You are Citizen Care's office complaint evidence validator.

    Your task is to compare an office complaint description
    with its uploaded photograph.

    Validate these conditions:

    1. Is the complaint related to office facilities,
       maintenance, cleanliness, equipment or safety?

    2. Does the photograph visibly show the reported problem?

    3. Is the photograph clear enough to verify the problem?

    Return ONLY valid JSON in this format:

    {
        "status": "valid",
        "relevant": true,
        "reason": "The photograph clearly shows a cracked dustbin."
    }

    Allowed status values:

    - valid: Complaint is relevant and photo supports it.
    - irrelevant: Complaint or photo is unrelated.
    - unclear: Photo is blurry, dark or insufficient.

    Rules:
    - Never guess details that cannot be seen.
    - Do not approve unrelated photographs.
    - Do not approve a complaint based only on its description.
    - If uncertain, return unclear.
    - Keep the reason short.
    """

    response = client.chat.completions.create(
        model="gpt-6-luna",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Complaint description: "
                            + complaint_description
                            + "\n\nValidate this uploaded photograph."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": "low"
                        }
                    }
                ]
            }
        ],
        max_completion_tokens=200,
        response_format={
            "type": "json_object"
        }
    )

    result = json.loads(
        response.choices[0].message.content
    )

    allowed_statuses = {
        "valid",
        "irrelevant",
        "unclear"
    }

    if result.get("status") not in allowed_statuses:
        raise ValueError("Invalid image validation status.")

    if not isinstance(result.get("relevant"), bool):
        raise ValueError("Invalid relevance result.")

    if not isinstance(result.get("reason"), str):
        raise ValueError("Invalid validation reason.")

    if result["status"] != "valid":
        result["relevant"] = False

    return result
