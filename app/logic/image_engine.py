import random
import time 
import requests
from app.config.settings import Config

class ImageEngine:
    BASE_URL = "https://api.deapi.ai/api/v1/client"
    def __init__(self):
        self.api_key = Config.DEAPI_KEY
        if not self.api_key:
            raise ValueError("Key missing check file or settings ")
        
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        model: str = "ZImageTurbo_INT8",
        width: int = 768,
        height: int = 768,
        guidance: float = 7.5,
        steps: int = 8,
        seed: int | None = None,
    ) -> dict: 
        """
        deAPI Text-to-Image:
        POST https://api.deapi.ai/api/v1/client/txt2img  -> request_id
        GET  https://api.deapi.ai/api/v1/client/request-status/{request_id} -> image URL
        Docs: txt2img + Get Results :contentReference[oaicite:5]{index=5}
        """
        if seed is None:
            seed = random.randint(0, 2_147_483_647)
        # phela job 
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "negative prompt",
            "model": model,
            "loras": [],          # future changes 
            "width": width,
            "height": height,
            "guidance": guidance,
            "steps": steps,
            "seed": seed,
        }
        
        
        resp = requests.post(
            f"{self.BASE_URL}/txt2img",
            json=payload,
            headers=self._headers(),
            timeout=60,
        )
        # print("DEAPI status:", resp.status_code)
        # print("DEAPI response text:", resp.text)

        resp.raise_for_status()
        data = resp.json()

        request_id = data.get("data", {}).get("request_id")
        if not request_id:
            raise RuntimeError(f"deAPI txt2img: request_id missing in response: {data}")

        image_url = None
        preview_url = None
        status = None

        for _ in range(20):
            status_resp = requests.get(
                f"{self.BASE_URL}/request-status/{request_id}",
                headers=self._headers(),
                timeout=30,
            )
            status_resp.raise_for_status()
            status_data = status_resp.json()
            d = status_data.get("data", {})

            status = d.get("status")
            preview_url = d.get("preview") or preview_url
            image_url = d.get("result_url") or d.get("result") or image_url

            if image_url and status not in {"pending", "queued"}:
                break

            time.sleep(1)

        if not image_url:
            #feedbaqck
            raise RuntimeError(
                f"deAPI: image not ready. status={status}, preview={preview_url}"
            )

        return {
                "request_id": request_id,
                "status": status,
                "image_url": image_url,
                "preview_url": preview_url,
        }