import json
import logging
from datetime import datetime, timezone
from markdown import markdown as md_convert

from ..extensions import db
from ..models.report import Report, ReportSection
from ..models.article import Article

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(self, ollama_client):
        self.ollama = ollama_client

    def generate_report(
        self,
        user_id: int,
        article_ids: list,
        report_type: str = "general",
        title: str = "",
        preferences: dict = None,
    ):
        articles = []
        for aid in article_ids:
            article = db.session.get(Article, aid)
            if article:
                articles.append(article.to_dict())

        if not articles:
            raise ValueError("No valid articles found")

        if not title:
            title = f"Report: {', '.join(a.get('title', '')[:50] for a in articles[:3])}"

        raw_country = preferences.get("preferred_countries", "global") if preferences else "global"
        if isinstance(raw_country, list):
            raw_country = ",".join(raw_country) if raw_country else "global"

        report = Report(
            user_id=user_id,
            title=title[:300],
            report_type=report_type,
            status="generating",
            article_ids=",".join(str(a["id"]) for a in articles),
            country=raw_country,
        )
        db.session.add(report)
        db.session.commit()

        try:
            content_md = self.ollama.generate_report(articles, report_type, preferences or {})
            self._parse_and_store(report, content_md)
            report.status = "completed"
            report.content_html = md_convert(content_md)
            summary = self._extract_summary(content_md)
            report.summary = summary
            db.session.commit()
        except Exception as e:
            logger.error("Report generation failed: %s", str(e))
            report.status = "failed"
            report.summary = f"Generation failed: {str(e)}"
            db.session.commit()

        return report

    def _parse_and_store(self, report: Report, content_md: str):
        sections = self._split_into_sections(content_md)
        for i, sec in enumerate(sections):
            section = ReportSection(
                report_id=report.id,
                title=sec.get("title", f"Section {i+1}"),
                content=sec.get("content", ""),
                order=i,
                section_type=sec.get("type", "text"),
            )
            db.session.add(section)

    def _split_into_sections(self, content_md: str):
        import re
        heading_pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
        sections = []
        last_pos = 0
        last_title = "Introduction"

        for match in heading_pattern.finditer(content_md):
            if match.start() > last_pos:
                body = content_md[last_pos : match.start()].strip()
                if body:
                    sections.append({"title": last_title, "content": body, "type": self._detect_type(body)})
            last_title = match.group(1).strip()
            last_pos = match.end()

        if last_pos < len(content_md):
            body = content_md[last_pos:].strip()
            if body:
                sections.append({"title": last_title, "content": body, "type": self._detect_type(body)})

        return sections

    def _detect_type(self, content: str):
        if "|" in content and "\n|" in content:
            return "table"
        if content.strip().startswith("- ") or content.strip().startswith("* "):
            return "list"
        return "text"

    def _extract_summary(self, content_md: str, max_chars: int = 300):
        import re
        clean = re.sub(r"[#*`\[\]()]", "", content_md)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean[:max_chars] + ("..." if len(clean) > max_chars else "")

    def get_report(self, report_id: int):
        report = db.session.get(Report, report_id)
        if not report:
            return None
        sections = ReportSection.query.filter_by(report_id=report_id).order_by(ReportSection.order).all()
        return {"report": report, "sections": sections}

    def get_user_reports(self, user_id: int, page: int = 1, per_page: int = 20):
        query = Report.query.filter_by(user_id=user_id).order_by(Report.created_at.desc())
        total = query.count()
        reports = query.offset((page - 1) * per_page).limit(per_page).all()
        return {"reports": reports, "total": total, "page": page}

    def delete_report(self, report_id: int, user_id: int):
        report = db.session.get(Report, report_id)
        if report and report.user_id == user_id:
            db.session.delete(report)
            db.session.commit()
            return True
        return False
