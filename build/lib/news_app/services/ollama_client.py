import json
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, config):
        self.host = config.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = config.get("OLLAMA_MODEL", "llama3.2")
        self.timeout = config.get("OLLAMA_TIMEOUT", 120)
        self._session = requests.Session()

    def _request(self, endpoint: str, payload: dict, stream: bool = False):
        url = f"{self.host}/api/{endpoint}"
        try:
            resp = self._session.post(
                url, json=payload, timeout=self.timeout, stream=stream
            )
            resp.raise_for_status()
            if stream:
                return resp
            return resp.json()
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama at %s", self.host)
            raise
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out after %ss", self.timeout)
            raise
        except requests.exceptions.RequestException as e:
            logger.error("Ollama request failed: %s", str(e))
            raise

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.3),
                "num_predict": kwargs.get("max_tokens", 2048),
            },
        }
        if system:
            payload["system"] = system

        response = self._request("generate", payload)
        logger.debug("Ollama generate response received (len=%d)", len(response.get("response", "")))
        return response.get("response", "")

    def generate_json(self, prompt: str, system: Optional[str] = None, **kwargs):
        raw = self.generate(prompt, system, **kwargs)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            json_match = __import__("re").search(r"\{.*\}", raw, __import__("re").DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Failed to parse JSON", "raw": raw}

    def generate_structured(self, prompt: str, output_schema: dict, **kwargs):
        system = (
            "You are a structured data extraction assistant. "
            "Respond ONLY with valid JSON matching the requested schema. "
            "Do not include any explanatory text outside the JSON."
        )
        schema_prompt = f"{prompt}\n\nRespond with JSON matching this schema: {json.dumps(output_schema)}"
        return self.generate_json(schema_prompt, system=system, **kwargs)

    def chat(self, messages: list, **kwargs):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.3),
                "num_predict": kwargs.get("max_tokens", 2048),
            },
        }
        response = self._request("chat", payload)
        return response.get("message", {}).get("content", "")

    def analyze_sentiment(self, text: str):
        prompt = (
            f"Analyze the sentiment of the following news text. "
            f"Respond with a JSON object containing: sentiment (positive/negative/neutral), "
            f"score (0.0 to 1.0), and key_phrases (list of 3-5 phrases).\n\nText: {text[:2000]}"
        )
        schema = {"sentiment": "string", "score": 0.0, "key_phrases": ["string"]}
        return self.generate_structured(prompt, schema)

    def summarize_article(self, title: str, content: str, max_words: int = 100):
        prompt = (
            f"Summarize this news article in {max_words} words or fewer. "
            f"Provide: 1) Main point 2) Key details 3) Implications.\n\n"
            f"Title: {title}\n\nContent: {content[:3000]}"
        )
        return self.generate(prompt, system="You are a professional news analyst. Be concise and factual.")

    def extract_risks(self, text: str):
        prompt = (
            f"Identify and tag risks mentioned in this text. "
            f"Respond with JSON: {{risks: [{{type: string, severity: string, description: string}}]}}.\n\n"
            f"Risk types include: regulatory_risk, market_volatility, liquidity_risk, credit_risk, "
            f"operational_risk, geopolitical_risk, technological_risk.\n\nText: {text[:3000]}"
        )
        schema = {"risks": [{"type": "string", "severity": "string", "description": "string"}]}
        return self.generate_structured(prompt, schema)

    def compare_articles(self, article1: dict, article2: dict):
        prompt = (
            f"Compare these two news articles and provide analysis. "
            f"Respond with JSON containing: common_themes, differences, "
            f"combined_sentiment, and key_insight.\n\n"
            f"Article 1: {json.dumps(article1)}\n\n"
            f"Article 2: {json.dumps(article2)}"
        )
        schema = {
            "common_themes": ["string"],
            "differences": ["string"],
            "combined_sentiment": "string",
            "key_insight": "string",
        }
        return self.generate_structured(prompt, schema)

    def explain_topic(self, topic: str, level: str = "simple"):
        prompt = (
            f"Explain '{topic}' in {level} terms. "
            f"Provide: overview, why it matters, and key things to know. "
            f"Format as clear paragraphs."
        )
        return self.generate(
            prompt,
            system="You are an expert educator who makes complex topics accessible.",
        )

    def generate_report(self, articles: list, report_type: str, preferences: dict):
        articles_summary = "\n\n".join(
            [
                f"Article {i+1}: {a.get('title', '')}\n"
                f"Source: {a.get('source_name', '')}\n"
                f"Date: {a.get('published_at', '')}\n"
                f"Region: {a.get('region', '')}\n"
                f"Summary: {a.get('description', '')[:500]}"
                for i, a in enumerate(articles[:10])
            ]
        )

        report_type_prompts = {
            "board_summary": (
                "Generate a board-level executive summary report. "
                "Include: executive summary, key developments, strategic implications, recommendations."
            ),
            "risk_memo": (
                "Generate a risk assessment memo. "
                "Include: risk overview, key risk factors (table format), probability assessment, "
                "mitigation strategies, monitoring recommendations."
            ),
            "market_overview": (
                "Generate a market overview report. "
                "Include: market summary, sector-wise breakdown (as table), trends, outlook."
            ),
            "financial_analysis": (
                "Generate a financial analysis report. "
                "Include: executive summary, key drivers, sector breakdown table, "
                "scenario analysis (best/base/worst case), risks, recommendations."
            ),
            "general": (
                "Generate a comprehensive analysis report. "
                "Include: executive summary, key findings, analysis, conclusions, recommendations."
            ),
        }

        prompt_template = report_type_prompts.get(report_type, report_type_prompts["general"])
        prompt = (
            f"{prompt_template}\n\n"
            f"User's preferred regions: {preferences.get('regions', 'global')}\n"
            f"User's preferred sectors: {preferences.get('sectors', 'general')}\n\n"
            f"Articles for analysis:\n{articles_summary}\n\n"
            f"Format the report in structured markdown with clear sections, "
            f"tables where appropriate, and bullet points. "
            f"Be data-driven and cite specific articles."
        )

        system = (
            "You are a senior financial analyst and report writer. "
            "Produce professional, well-structured reports suitable for C-suite and board-level readers. "
            "Be precise, data-driven, and actionable."
        )

        return self.generate(prompt, system=system, temperature=0.2, max_tokens=4096)
