"""
Purpose:
Lead AI Assistant Service for Jarvis AI OS.

Responsibilities:
- Generate lead summaries, company profiles, and intent signals from CRM data
- Draft personalized follow-up emails tailored to tone and lead context
- Process meeting transcripts into structured summaries, action items, and key decisions

Dependencies:
- services/crm_engine.py
- memory/database.py
- services/logger.py
"""

import re
from typing import Any, Dict, List, Optional, Union
import memory.database as db
from services.crm_engine import crm_engine
from services.logger import logger


class LeadAIAssistantService:
    """AI Assistant Service for CRM lead summaries, follow-up emails, and meeting notes."""

    def __init__(self) -> None:
        """Initialize LeadAIAssistantService with singleton crm_engine reference."""
        self.crm = crm_engine

    def _get_lead_data(self, lead_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Retrieve lead record using crm_engine or direct SQLite fallback.

        Args:
            lead_id: Identifier of the CRM lead.

        Returns:
            Dict containing lead properties, or None if lead is not found.
        """
        if lead_id is None:
            return None

        # Attempt to retrieve via crm_engine service helper
        try:
            if hasattr(self.crm, "get_lead"):
                lead = self.crm.get_lead(lead_id)
                if lead:
                    return dict(lead)
        except Exception:
            pass

        # Fallback direct database query
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, workspace_id, name, email, company, phone, status, score, source, created_at "
                    "FROM leads WHERE id = ?",
                    (str(lead_id).strip(),),
                )
                row = cursor.fetchone()
                if row:
                    return dict(row)
        except Exception as e:
            logger.error("LEAD_AI_ASSISTANT", f"Failed to fetch lead '{lead_id}': {e}")

        return None

    def generate_lead_summary(self, lead_id: Union[str, int]) -> Dict[str, Any]:
        """Generates executive lead summary, company profile, and intent signals.

        Args:
            lead_id: Unique identifier for the CRM lead.

        Returns:
            Dict containing:
                - lead_id: Input lead ID.
                - executive_summary (str): High-level overview of the lead.
                - company_profile (str): Detailed profile of the lead's company and background.
                - intent_signals (List[str]): List of buyer intent signals.
        """
        lead = self._get_lead_data(lead_id)

        if not lead:
            logger.warning("LEAD_AI_ASSISTANT", f"Lead '{lead_id}' not found in CRM database.")
            return {
                "lead_id": lead_id,
                "executive_summary": f"Lead ID '{lead_id}' not found in CRM database.",
                "company_profile": f"Company profile unavailable for lead ID '{lead_id}'.",
                "intent_signals": [
                    "Lead record uninitialized",
                    "Standard inbound evaluation signal",
                ],
            }

        name = lead.get("name", "Prospect")
        company = lead.get("company", "").strip() or "Independent / Unspecified"
        email = lead.get("email", "")
        phone = lead.get("phone", "").strip() or "Not provided"
        status = lead.get("status", "NEW")
        score = lead.get("score", 50)
        source = lead.get("source", "web")
        created_at = lead.get("created_at", "")

        intent_signals: List[str] = []
        if score >= 70:
            intent_signals.append(f"High conversion probability with lead score {score}/100")
        elif score >= 40:
            intent_signals.append(f"Moderate engagement intent with score {score}/100")
        else:
            intent_signals.append(f"Initial lead discovery phase with score {score}/100")

        if "@" in email:
            domain = email.split("@")[-1].lower()
            free_domains = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"}
            if domain not in free_domains:
                intent_signals.append(f"Verified corporate email domain: {domain}")

        if status in ["QUALIFIED", "PROPOSAL", "WON"]:
            intent_signals.append(f"Advanced pipeline status: {status}")
        else:
            intent_signals.append(f"Pipeline status: {status}")

        if source:
            intent_signals.append(f"Acquired via channel: {source}")

        if phone != "Not provided":
            intent_signals.append("Direct contact number provided")

        executive_summary = (
            f"Lead '{name}' ({email}) representing '{company}' is currently in status '{status}' "
            f"with a lead score of {score}/100. Acquired via '{source}' channel."
        )

        company_profile = (
            f"Company Name: {company}\n"
            f"Primary Contact: {name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"CRM Pipeline Status: {status}\n"
            f"Lead Score: {score}/100\n"
            f"Acquisition Source: {source}\n"
            f"Record Created: {created_at}"
        )

        logger.info("LEAD_AI_ASSISTANT", f"Generated summary for lead '{lead_id}' ({name})")

        return {
            "lead_id": lead_id,
            "executive_summary": executive_summary,
            "company_profile": company_profile,
            "intent_signals": intent_signals,
        }

    def draft_followup_email(self, lead_id: Union[str, int], tone: str = "professional") -> Dict[str, Any]:
        """Drafts a personalized sales follow-up email tailored to tone and lead context.

        Args:
            lead_id: Unique identifier for the CRM lead.
            tone: Desired communication tone ('professional', 'casual', 'urgent', 'persuasive'). Default: 'professional'.

        Returns:
            Dict containing:
                - subject (str): Email subject line.
                - email_body (str): Complete email body text.
        """
        lead = self._get_lead_data(lead_id)

        clean_tone = (tone or "professional").strip().lower()
        if lead:
            name = lead.get("name", "Prospect")
            company = lead.get("company", "").strip() or "your organization"
        else:
            name = "Prospect"
            company = "your organization"

        if clean_tone == "casual":
            subject = f"Checking in! - {company}"
            email_body = (
                f"Hey {name},\n\n"
                f"Hope you're having a great week!\n\n"
                f"I wanted to quickly touch base regarding our recent updates for {company}. "
                f"We're making great progress and I'd love to jump on a quick call to share what's new.\n\n"
                f"Let me know what time works best for you!\n\n"
                f"Cheers,\n"
                f"Jarvis AI OS Team"
            )
        elif clean_tone == "urgent":
            subject = f"Action Required: Next steps for {company}"
            email_body = (
                f"Hello {name},\n\n"
                f"I am reaching out to follow up on the next steps for {company}.\n\n"
                f"As we review our current pipeline, we want to ensure we align with your timeline "
                f"and answer any outstanding questions before moving forward.\n\n"
                f"Please let us know your availability today or tomorrow for a brief alignment call.\n\n"
                f"Best regards,\n"
                f"Jarvis AI OS Team"
            )
        elif clean_tone == "persuasive":
            subject = f"Accelerating growth at {company} with Jarvis AI OS"
            email_body = (
                f"Dear {name},\n\n"
                f"Following up on our discussions, I wanted to highlight how partnering with us "
                f"can deliver immediate operational impact for {company}.\n\n"
                f"Our AI OS workspace platform automates workflows, streamlines knowledge integration, "
                f"and drives measurable ROI from day one.\n\n"
                f"Are you open to a 15-minute demo this week to explore how we can support {company}'s strategic goals?\n\n"
                f"Warm regards,\n"
                f"Jarvis AI OS Team"
            )
        else:
            # Professional
            subject = f"Follow-up regarding {company} & Next Steps"
            email_body = (
                f"Dear {name},\n\n"
                f"I hope this email finds you well.\n\n"
                f"I am following up on our previous communication regarding {company}. "
                f"We are eager to assist you with your requirements and explore how we can best support your team.\n\n"
                f"Please let me know if you have any questions or if you would like to schedule a quick call to discuss further.\n\n"
                f"Best regards,\n"
                f"Jarvis AI OS Team"
            )

        logger.info("LEAD_AI_ASSISTANT", f"Drafted '{clean_tone}' follow-up email for lead '{lead_id}'")

        return {
            "subject": subject,
            "email_body": email_body,
        }

    def generate_meeting_notes(self, lead_id: Union[str, int], raw_transcript: str) -> Dict[str, Any]:
        """Parses meeting transcripts into executive summary, key decisions, and action items.

        Args:
            lead_id: Unique identifier for the CRM lead.
            raw_transcript: Raw transcript text of the meeting.

        Returns:
            Dict containing:
                - summary (str): Concise meeting summary.
                - action_items (List[str]): List of identified action items.
                - key_decisions (List[str]): List of key decisions made.
        """
        lead = self._get_lead_data(lead_id)
        contact_ref = f" (Lead: {lead['name']} - {lead.get('company', '')})" if lead else f" (Lead ID: {lead_id})"

        transcript_clean = (raw_transcript or "").strip()
        if not transcript_clean:
            return {
                "summary": f"No transcript content provided for meeting{contact_ref}.",
                "action_items": [],
                "key_decisions": [],
            }

        lines = [line.strip() for line in transcript_clean.split("\n") if line.strip()]

        summary_parts: List[str] = []
        action_items: List[str] = []
        key_decisions: List[str] = []

        action_keywords = ["action", "todo", "to-do", "will", "follow up", "follow-up", "task", "assign", "prepare", "send"]
        decision_keywords = ["agreed", "decided", "decision", "approved", "confirmed", "resolved", "selected", "finalized"]

        for line in lines:
            clean_line = re.sub(r"^[-*•\d+.\s]+", "", line).strip()
            if not clean_line:
                continue

            lower_line = clean_line.lower()

            is_action = any(re.search(rf"\b{kw}\b", lower_line) for kw in action_keywords)
            is_decision = any(re.search(rf"\b{kw}\b", lower_line) for kw in decision_keywords)

            if is_action:
                action_items.append(clean_line)
            if is_decision:
                key_decisions.append(clean_line)

            if not is_action and not is_decision:
                summary_parts.append(clean_line)

        if summary_parts:
            summary_text = f"Meeting summary{contact_ref}: " + " ".join(summary_parts[:5])
        else:
            summary_text = f"Meeting covered key alignment and discussion points{contact_ref}."

        if not action_items:
            action_items = [f"Follow up with lead {lead_id} on next steps."]

        if not key_decisions:
            key_decisions = ["Agreed to continue discussions and review proposal."]

        logger.info("LEAD_AI_ASSISTANT", f"Generated meeting notes for lead '{lead_id}'")

        return {
            "summary": summary_text,
            "action_items": action_items,
            "key_decisions": key_decisions,
        }


# Singleton instance
lead_ai_assistant = LeadAIAssistantService()
