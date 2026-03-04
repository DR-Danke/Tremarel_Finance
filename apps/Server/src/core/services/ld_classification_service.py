"""Legal Desk AI classification service for case domain, type, and complexity."""

import json
from decimal import Decimal

from sqlalchemy.orm import Session

from src.config.settings import get_settings
from src.interface.legaldesk_dto import (
    CaseComplexity,
    CaseType,
    ClassificationResultDTO,
    LegalDomain,
)
from src.repository.ld_case_repository import ld_case_repository

# Keyword mappings for fallback classification
DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "corporate": ["merger", "acquisition", "shareholder", "board", "incorporation", "corporate"],
    "ip": ["patent", "trademark", "copyright", "intellectual property", "brand"],
    "labor": ["employment", "worker", "termination", "labor", "harassment", "wage"],
    "tax": ["tax", "fiscal", "irs", "deduction", "filing"],
    "litigation": ["lawsuit", "court", "dispute", "damages", "trial"],
    "real_estate": ["property", "lease", "tenant", "landlord", "zoning"],
    "immigration": ["visa", "immigration", "citizenship", "deportation", "asylum"],
    "regulatory": ["compliance", "regulation", "license", "permit", "inspection"],
    "data_privacy": ["privacy", "gdpr", "data protection", "breach", "consent"],
    "commercial": ["contract", "agreement", "vendor", "procurement", "negotiation"],
}


class LdClassificationService:
    """Service for AI-powered legal case classification."""

    def classify_case(self, db: Session, case_id: int) -> ClassificationResultDTO:
        """
        Classify a legal case by domain, type, complexity, and confidence.

        Uses OpenAI GPT-4o-mini when API key is available, falls back to
        keyword-based classification otherwise.

        Args:
            db: Database session
            case_id: Case primary key

        Returns:
            ClassificationResultDTO with classification results

        Raises:
            ValueError: If case not found
        """
        print(f"INFO [LdClassificationService]: Classifying case {case_id}")

        case = ld_case_repository.get_by_id(db, case_id)
        if not case:
            print(f"ERROR [LdClassificationService]: Case {case_id} not found")
            raise ValueError(f"Case with id {case_id} not found")

        text = f"{case.title} {case.description or ''}"
        print(f"INFO [LdClassificationService]: Classification text: '{text[:100]}...'")

        settings = get_settings()
        result: ClassificationResultDTO

        if settings.OPENAI_API_KEY:
            try:
                print("INFO [LdClassificationService]: Using OpenAI classification")
                result = self._classify_with_openai(text)
            except Exception as e:
                print(f"WARN [LdClassificationService]: OpenAI failed ({e}), falling back to keywords")
                result = self._classify_with_keywords(text)
        else:
            print("INFO [LdClassificationService]: No OPENAI_API_KEY, using keyword classification")
            result = self._classify_with_keywords(text)

        # Persist classification to case
        result_dict = {
            "legal_domain": result.legal_domain.value,
            "complexity": result.complexity.value,
            "case_type": result.case_type.value,
            "confidence": str(result.confidence),
            "suggested_tags": result.suggested_tags,
        }
        ld_case_repository.update(db, case_id, {"ai_classification": result_dict})
        print(f"INFO [LdClassificationService]: Classification stored for case {case_id}")

        return result

    def _classify_with_openai(self, text: str) -> ClassificationResultDTO:
        """
        Classify text using OpenAI GPT-4o-mini.

        Args:
            text: Combined title and description text

        Returns:
            ClassificationResultDTO from AI response

        Raises:
            Exception: On OpenAI API errors or invalid JSON response
        """
        from openai import OpenAI

        settings = get_settings()
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        domain_values = ", ".join(d.value for d in LegalDomain)
        type_values = ", ".join(t.value for t in CaseType)
        complexity_values = ", ".join(c.value for c in CaseComplexity)

        system_prompt = (
            "You are a legal case classifier. Analyze the case text and return a JSON object with:\n"
            f"- legal_domain: one of [{domain_values}]\n"
            f"- case_type: one of [{type_values}]\n"
            f"- complexity: one of [{complexity_values}]\n"
            "- confidence: a decimal between 0 and 1\n"
            "- reasoning: a brief explanation of your classification\n"
            "Return ONLY valid JSON, no markdown."
        )

        print("INFO [LdClassificationService]: Sending request to OpenAI GPT-4o-mini")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content
        print(f"INFO [LdClassificationService]: OpenAI response: {content}")
        parsed = json.loads(content)

        return ClassificationResultDTO(
            legal_domain=LegalDomain(parsed["legal_domain"]),
            complexity=CaseComplexity(parsed["complexity"]),
            case_type=CaseType(parsed["case_type"]),
            confidence=Decimal(str(parsed["confidence"])),
            suggested_tags=[parsed.get("reasoning", "")] if parsed.get("reasoning") else [],
        )

    def _classify_with_keywords(self, text: str) -> ClassificationResultDTO:
        """
        Classify text using keyword frequency matching.

        Args:
            text: Combined title and description text

        Returns:
            ClassificationResultDTO with keyword-based classification
        """
        print("INFO [LdClassificationService]: Running keyword-based classification")
        text_lower = text.lower()

        # Count keyword matches per domain
        domain_scores: dict[str, int] = {}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                domain_scores[domain] = score

        # Select best domain, default to commercial
        if domain_scores:
            best_domain = max(domain_scores, key=lambda d: domain_scores[d])
        else:
            best_domain = "commercial"

        print(f"INFO [LdClassificationService]: Keyword scores: {domain_scores}, selected: {best_domain}")

        # Determine case type
        case_type = CaseType.LITIGATION if best_domain == "litigation" else CaseType.ADVISORY

        return ClassificationResultDTO(
            legal_domain=LegalDomain(best_domain),
            complexity=CaseComplexity.MEDIUM,
            case_type=case_type,
            confidence=Decimal("0.5"),
            suggested_tags=[],
        )


# Singleton instance
ld_classification_service = LdClassificationService()
