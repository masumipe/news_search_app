import gradio as gr
import logging
from ..services.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


def create_interfaces(ollama_client: OllamaClient):
    def ask_ai_about_article(article_text, question):
        if not article_text or not question:
            return "Please provide both article text and a question."
        prompt = (
            f"Based on this article:\n\n{article_text[:2000]}\n\n"
            f"Answer this question: {question}\n\n"
            f"Be concise and factual, citing specific parts of the article."
        )
        return ollama_client.generate(
            prompt,
            system="You are an AI assistant specialized in news analysis.",
            temperature=0.3,
        )

    def compare_two_stories(story1, story2):
        if not story1 or not story2:
            return "Please provide both stories."
        article1 = {"title": "Story 1", "description": story1[:1500]}
        article2 = {"title": "Story 2", "description": story2[:1500]}
        result = ollama_client.compare_articles(article1, article2)
        if isinstance(result, dict):
            lines = [
                f"**Common Themes:** {', '.join(result.get('common_themes', []))}",
                f"**Differences:** {', '.join(result.get('differences', []))}",
                f"**Combined Sentiment:** {result.get('combined_sentiment', 'N/A')}",
                f"**Key Insight:** {result.get('key_insight', 'N/A')}",
            ]
            return "\n\n".join(lines)
        return str(result)

    def explain_topic(topic, complexity):
        if not topic:
            return "Please provide a topic."
        level_map = {"Simple": "simple", "Moderate": "moderate", "Expert": "expert"}
        return ollama_client.explain_topic(topic, level_map.get(complexity, "simple"))

    def analyze_sentiment_ui(text):
        if not text:
            return "Please provide text.", ""
        result = ollama_client.analyze_sentiment(text[:2000])
        sentiment = result.get("sentiment", "unknown")
        score = result.get("score", 0)
        phrases = result.get("key_phrases", [])
        summary = f"Sentiment: **{sentiment.upper()}** (score: {score:.2f})"
        details = f"Key phrases: {', '.join(phrases)}" if phrases else ""
        return summary, details

    grade_map = {
        0: "High School",
        1: "College",
        2: "PhD",
    }

    with gr.Blocks(title="NewsAI Analytics Tools", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# NewsAI - AI-Powered Analytics Tools")
        gr.Markdown("Leverage local LLM (Ollama) for advanced news analysis.")

        with gr.Tab("Ask the AI"):
            with gr.Row():
                with gr.Column():
                    article_input = gr.Textbox(
                        label="Article Text",
                        placeholder="Paste the article content here...",
                        lines=8,
                    )
                    question_input = gr.Textbox(
                        label="Your Question",
                        placeholder="e.g., What are the main risks mentioned?",
                    )
                    ask_btn = gr.Button("Ask AI", variant="primary")
                with gr.Column():
                    answer_output = gr.Markdown(label="AI Answer")

            ask_btn.click(ask_ai_about_article, [article_input, question_input], answer_output)

        with gr.Tab("Compare Stories"):
            with gr.Row():
                with gr.Column():
                    story1_input = gr.Textbox(
                        label="Story 1", placeholder="Paste first news story...", lines=6
                    )
                with gr.Column():
                    story2_input = gr.Textbox(
                        label="Story 2", placeholder="Paste second news story...", lines=6
                    )
            compare_btn = gr.Button("Compare", variant="primary")
            compare_output = gr.Markdown(label="Comparison")

            compare_btn.click(compare_two_stories, [story1_input, story2_input], compare_output)

        with gr.Tab("Explain Topic"):
            with gr.Row():
                with gr.Column():
                    topic_input = gr.Textbox(
                        label="Topic",
                        placeholder="e.g., Quantitative Easing, Supply Chain, ESG Investing",
                    )
                    complexity = gr.Radio(
                        ["Simple", "Moderate", "Expert"],
                        label="Complexity Level",
                        value="Simple",
                    )
                    explain_btn = gr.Button("Explain", variant="primary")
                with gr.Column():
                    explain_output = gr.Markdown(label="Explanation")

            explain_btn.click(explain_topic, [topic_input, complexity], explain_output)

        with gr.Tab("Sentiment Analysis"):
            with gr.Row():
                with gr.Column():
                    sentiment_input = gr.Textbox(
                        label="Text to Analyze",
                        placeholder="Paste article text or paragraph...",
                        lines=8,
                    )
                    sentiment_btn = gr.Button("Analyze Sentiment", variant="primary")
                with gr.Column():
                    sentiment_output = gr.Markdown(label="Result")
                    phrases_output = gr.Textbox(label="Key Phrases")

            sentiment_btn.click(
                analyze_sentiment_ui,
                [sentiment_input],
                [sentiment_output, phrases_output],
            )

        gr.Markdown(
            "---\n*These tools use Ollama local LLM. All processing happens on your machine.*"
        )

    return demo
