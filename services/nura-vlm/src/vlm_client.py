"""
Ollama VLM Client
Handles communication with Ollama API for vision-language model inference
"""
import httpx
import base64
import logging
from typing import Optional, Dict, Any
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


class OllamaVLMClient:
    """Client for Ollama Vision-Language Model API"""

    def __init__(self, base_url: str = "http://ollama:11434", model: str = "llava:13b"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=180.0)

    async def health_check(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    async def list_models(self) -> list:
        """List available models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    async def generate_with_image(
        self,
        prompt: str,
        image_base64: str,
        temperature: float = 0.3,
        max_tokens: int = 500
    ) -> Optional[str]:
        """
        Generate text response from image and prompt using VLM

        Args:
            prompt: Text prompt/question about the image
            image_base64: Base64-encoded image
            temperature: Sampling temperature (0-1, lower = more consistent)
            max_tokens: Maximum tokens in response

        Returns:
            Generated text response or None if error
        """
        try:
            # Prepare request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }

            logger.info(f"Sending VLM request to {self.base_url}/api/generate")
            logger.debug(f"Model: {self.model}, Prompt length: {len(prompt)}")

            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )

            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None

            data = response.json()
            response_text = data.get("response", "")

            logger.info(f"VLM response received: {len(response_text)} chars")
            logger.debug(f"Response preview: {response_text[:200]}")

            return response_text

        except httpx.TimeoutException:
            logger.error("VLM request timed out (>180s)")
            return None
        except Exception as e:
            logger.error(f"VLM generation failed: {e}")
            return None

    async def analyze_scene(
        self,
        image_base64: str,
        prompt: str,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Analyze a scene with structured prompt

        Returns dict with:
        - raw_response: Full VLM response text
        - parsed: Dict with extracted fields (if possible)
        """
        response_text = await self.generate_with_image(
            prompt=prompt,
            image_base64=image_base64,
            temperature=temperature
        )

        if not response_text:
            return {
                "raw_response": None,
                "parsed": {},
                "error": "VLM generation failed"
            }

        # Attempt to parse response
        parsed = self._parse_response(response_text, prompt)

        return {
            "raw_response": response_text,
            "parsed": parsed,
            "error": None
        }

    def _parse_response(self, response: str, prompt: str) -> Dict[str, Any]:
        """
        Attempt to extract structured data from VLM response

        Looks for patterns like:
        - "Yes" / "No" for boolean questions
        - Numbers for counting questions
        - Keywords for classification
        """
        response_lower = response.lower()
        parsed = {}

        # Check for supervision
        if "adult" in prompt.lower():
            if any(word in response_lower for word in ["no adult", "no adults", "not visible", "cannot see"]):
                parsed["adults_detected"] = False
            elif any(word in response_lower for word in ["adult visible", "adult present", "teacher", "staff"]):
                parsed["adults_detected"] = True

        # Check for count
        if "how many" in prompt.lower() or "count" in prompt.lower():
            # Try to extract first number
            words = response.split()
            for word in words:
                if word.isdigit():
                    parsed["count"] = int(word)
                    break

        # Check for safety concerns
        concern_keywords = ["concern", "concerning", "unsafe", "danger", "risk", "hazard", "violation"]
        if any(keyword in response_lower for keyword in concern_keywords):
            parsed["safety_concern"] = True
        elif any(word in response_lower for word in ["safe", "appropriate", "normal", "fine"]):
            parsed["safety_concern"] = False

        return parsed

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Predefined prompt templates
PROMPT_TEMPLATES = {
    "supervision": """Analyze this classroom scene carefully.

Question: Is there an adult (teacher, staff member, or caregiver) visible in this image who is supervising the children?

Look for:
- Adults present in the room
- Their proximity to children
- Whether they appear to be actively supervising

Answer with:
1. Yes or No
2. A brief explanation of what you see (adults, children, their activities)

Be specific and factual.""",

    "count_children": """Count the number of children visible in this image.

Instructions:
- Count only children (not adults)
- Count partially visible children if you can clearly identify them
- State the number first, then briefly describe what you see

Answer format:
Number: [X]
Description: [brief description]""",

    "behavior_analysis": """Analyze the behavior and interactions in this childcare scene.

Look for:
1. Physical interactions between people
2. Emotional states (calm, distressed, engaged)
3. Any concerning behaviors (aggression, distress, inappropriate contact)
4. Safety hazards or risks

Describe what you observe objectively and flag any concerns.""",

    "restricted_area": """Analyze this image to determine the type of area shown.

Questions:
1. What type of room or area is this? (classroom, kitchen, bathroom, storage, office, playground, etc.)
2. Are there any children present?
3. Is this an area where children should be allowed?

Look for clues like equipment, furniture, signage, and layout.
Answer objectively based on what you can see.""",

    "safety_hazard": """Identify any safety hazards in this childcare environment.

Look for:
- Open doors to restricted/dangerous areas
- Sharp or dangerous objects within reach
- Spills or trip hazards
- Unsecured furniture
- Broken equipment
- Overcrowding
- Fire exits blocked

List any hazards you identify, or state "No obvious hazards visible" if the scene appears safe.""",

    "capacity_check": """Assess whether this room appears overcrowded.

Consider:
- Available floor space
- Number of people present
- Type of activity
- Age-appropriate space requirements

Answer:
1. Does this room appear overcrowded? (Yes/No/Cannot determine)
2. Estimate the number of children and adults visible
3. Brief explanation of your assessment""",
}
