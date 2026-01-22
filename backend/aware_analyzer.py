import math
import re
import statistics
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Dict, List, Optional

from .parsers import WORD_RE, count_words
from .advanced_features import (
    calculate_lexical_diversity,
    calculate_readability_scores,
    calculate_ngram_repetition,
    calculate_burstiness,
    bayesian_score_adjustment,
    detect_pattern_correlations,
    calculate_entropy,
    detect_anomalies,
    calculate_contextual_adjustments,
)

# Try to import NLTK for NLP tasks
try:
    import nltk
    from nltk.tokenize import sent_tokenize
    from nltk import pos_tag, word_tokenize
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)

    NLTK_AVAILABLE = True
    POS_AVAILABLE = True
except Exception:
    NLTK_AVAILABLE = False
    POS_AVAILABLE = False


QUOTE_STRAIGHT_RE = re.compile(r"[\"']")
QUOTE_SMART_RE = re.compile(r"[“”‘’]")


@dataclass
class MarkerResult:
    marker_id: str
    category: str
    name: str
    count: int
    score: float
    max_contribution: float
    evidence: List[Dict]
    description: str

    def to_dict(self) -> Dict:
        return {
            "id": self.marker_id,
            "name": self.name,
            "count": self.count,
            "score": round(self.score, 2),
            "max_contribution": self.max_contribution,
            "evidence": self.evidence,
            "description": self.description,
        }


CATEGORY_WEIGHTS = {
    "A": 0.30,
    "B": 0.15,
    "C": 0.15,
    "D": 0.05,
    "E": 0.10,
    "F": 0.08,
    "G": 0.07,
    "H": 0.05,
    "I": 0.03,
    "J": 0.02,
}

CATEGORY_CAPS = {
    "A": 450,
    "B": 270,
    "C": 225,
    "D": 125,
    "E": 155,
    "F": 100,
    "G": 125,
    "H": 180,
    "I": 120,
    "J": 105,
}


def analyze_document(doc_data: Dict, original_doc: Optional[Dict] = None) -> Dict:
    text = doc_data.get("text") or ""
    paragraphs = doc_data.get("paragraphs") or []
    word_count = count_words(text)

    # Use NLTK for sentence tokenization
    if NLTK_AVAILABLE:
        sentences = sent_tokenize(text)
    else:
        # Fallback to simple sentence splitting
        sentences = re.split(r'[.!?]+\s+', text)
    sentences = [sent.strip() for sent in sentences if sent.strip()]

    document_type = detect_document_type(text)

    marker_results: List[MarkerResult] = []
    marker_counts: Dict[str, float] = {}

    marker_results.extend(detect_category_a(text, word_count, paragraphs, marker_counts))
    marker_results.extend(detect_category_b(text, word_count, sentences, marker_counts))
    marker_results.extend(
        detect_category_c(
            text,
            word_count,
            doc_data,
            original_doc,
            marker_counts,
        )
    )
    marker_results.extend(detect_category_d(text, word_count, sentences, marker_counts))
    marker_results.extend(detect_category_e(text, paragraphs, marker_counts))
    marker_results.extend(detect_category_f(text, paragraphs, sentences, marker_counts))
    marker_results.extend(detect_category_g(text, sentences, marker_counts))
    marker_results.extend(detect_category_h(doc_data, word_count, marker_counts))
    marker_results.extend(detect_category_i(text, paragraphs, sentences, marker_counts))
    marker_results.extend(detect_category_j(doc_data, paragraphs, marker_counts))

    category_scores: Dict[str, float] = {key: 0.0 for key in CATEGORY_WEIGHTS}
    categories: Dict[str, Dict] = {key: {"score": 0.0, "markers": []} for key in CATEGORY_WEIGHTS}
    evidence: List[Dict] = []

    for marker in marker_results:
        capped_score = min(marker.score, marker.max_contribution)
        marker.score = capped_score
        category_scores[marker.category] += capped_score
        categories[marker.category]["markers"].append(marker.to_dict())
        if marker.evidence:
            for snippet in marker.evidence:
                evidence.append(
                    {
                        "marker_id": marker.marker_id,
                        "text": snippet.get("text"),
                        "index": snippet.get("index"),
                    }
                )

    for cat, score in category_scores.items():
        category_scores[cat] = min(score, CATEGORY_CAPS[cat])
        categories[cat]["score"] = round(category_scores[cat], 2)

    weighted_score, max_weighted = calculate_weighted_score(category_scores)
    base_score = (weighted_score / max_weighted) * 100 if max_weighted else 0.0

    composite_patterns = check_composite_patterns(marker_counts)
    composite_bonus = sum(p["bonus"] for p in composite_patterns)
    base_score = min(100.0, base_score + composite_bonus)

    # Advanced feature extraction
    lexical_diversity = calculate_lexical_diversity(text)
    readability = calculate_readability_scores(text, sentences)
    ngram_repetition = calculate_ngram_repetition(text, n=3)
    burstiness = calculate_burstiness(sentences)
    text_entropy = calculate_entropy(text)
    anomalies = detect_anomalies(text, sentences, paragraphs)
    pattern_correlations = detect_pattern_correlations(marker_counts)

    # Apply advanced scoring adjustments
    base_score = min(100.0, base_score + pattern_correlations["correlation_bonus"])
    base_score = min(100.0, base_score + anomalies["anomaly_score"])

    # Lexical diversity scoring (low diversity = more AI-like)
    if lexical_diversity["type_token_ratio"] < 0.35:
        base_score += 8
    if lexical_diversity["mtld"] < 50:
        base_score += 12
    if lexical_diversity["hapax_legomena_ratio"] < 0.25:
        base_score += 6

    # Burstiness scoring (low burstiness = more AI-like)
    if burstiness["burstiness_score"] < 0.3:
        base_score += 10
    if burstiness["complexity_variation"] < 3.0:
        base_score += 8

    # N-gram repetition scoring
    if ngram_repetition["repetition_score"] > 15:
        base_score += 15
    elif ngram_repetition["repetition_score"] > 8:
        base_score += 8

    # Entropy scoring (lower entropy = more predictable/AI-like)
    if text_entropy < 4.0:
        base_score += 10

    # Readability consistency check (too consistent = AI-like)
    readability_scores = [
        readability["flesch_kincaid_grade"],
        readability["gunning_fog"],
        readability["coleman_liau_index"],
    ]
    if len(readability_scores) >= 3:
        readability_std = statistics.pstdev(readability_scores)
        if readability_std < 2.0:  # Very consistent readability
            base_score += 7

    base_score = min(100.0, base_score)

    human_indicators, human_reduction = detect_human_indicators(
        text, sentences, word_count, doc_data
    )
    base_score = max(0.0, base_score - human_reduction)

    markers_found = sum(1 for m in marker_results if m.score > 0)
    confidence_data = adjust_for_confidence(base_score, word_count, markers_found)
    adjusted_score = confidence_data["adjusted_score"]

    # Apply Bayesian reasoning
    bayesian_result = bayesian_score_adjustment(
        adjusted_score, marker_counts, document_type, word_count
    )
    bayesian_score = bayesian_result["bayesian_adjusted_score"]

    # Apply contextual adjustments to reduce false positives
    contextual_result = calculate_contextual_adjustments(
        bayesian_score, document_type, word_count, marker_counts, readability
    )
    final_adjusted_score = contextual_result["adjusted_score"]

    # Use weighted average instead of minimum (more balanced approach)
    # Weight: confidence_adjusted (40%), bayesian (40%), contextual (20%)
    adjusted_score = (
        adjusted_score * 0.4 +
        bayesian_score * 0.4 +
        final_adjusted_score * 0.2
    )

    # Enhanced confidence calculation
    base_confidence = confidence_data["confidence"]
    bayesian_confidence = bayesian_result["bayesian_confidence"]
    # Weight multiple confidence factors
    enhanced_confidence = (
        base_confidence * 0.4 +
        bayesian_confidence * 0.3 +
        (1.0 if markers_found >= 5 else 0.7) * 0.3
    )
    confidence_label = confidence_level(enhanced_confidence)

    high_confidence_markers = sum(
        1 for m in marker_results if m.category == "A" and m.score > 0
    )
    classification = classify_risk(adjusted_score, high_confidence_markers)
    classification = apply_composite_override(classification, composite_patterns)

    recommendation = recommendation_for_classification(classification)

    return {
        "score": round(adjusted_score, 1),
        "classification": classification,
        "confidence": confidence_label,
        "categories": categories,
        "composite_patterns": composite_patterns,
        "human_indicators": human_indicators,
        "evidence": evidence,
        "recommendation": recommendation,
        "advanced_analysis": {
            "lexical_diversity": lexical_diversity,
            "readability_metrics": readability,
            "ngram_repetition": ngram_repetition,
            "burstiness": burstiness,
            "text_entropy": text_entropy,
            "statistical_anomalies": anomalies,
            "pattern_correlations": pattern_correlations,
            "bayesian_analysis": {
                "posterior_probability": bayesian_result["posterior_probability"],
                "prior_probability": bayesian_result["prior_probability"],
                "likelihood_ratio": bayesian_result["likelihood_ratio"],
            },
            "contextual_adjustments": contextual_result["contextual_adjustments"],
        },
        "scoring_breakdown": {
            "base_score": round(base_score, 1),
            "composite_bonus": composite_bonus,
            "correlation_bonus": pattern_correlations["correlation_bonus"],
            "anomaly_bonus": anomalies["anomaly_score"],
            "human_reduction": human_reduction,
            "bayesian_adjusted": round(bayesian_score, 1),
            "contextual_adjusted": round(final_adjusted_score, 1),
            "final_score": round(adjusted_score, 1),
        },
        "meta": {
            "analysis_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "2.0_enhanced",
            "document": {
                "filename": doc_data.get("filename"),
                "word_count": word_count,
                "paragraph_count": len(paragraphs),
                "sentence_count": len(sentences),
                "document_type": document_type,
                "has_original": original_doc is not None,
                "has_track_changes": bool(doc_data.get("track_changes")),
                "has_timing_data": bool(doc_data.get("metadata", {}).get("editing_minutes")),
            },
        },
    }


def detect_category_a(
    text: str, word_count: int, paragraphs: List[str], marker_counts: Dict
) -> List[MarkerResult]:
    results = []

    # A1 Em-dash usage
    matches = list(re.finditer(r"—|--", text))
    count = len(matches)
    if count <= 2:
        score = 0
    elif count <= 5:
        score = (count - 2) * 15
    else:
        score = 45 + (count - 5) * 20
    evidence = build_snippets(text, matches)
    results.append(
        MarkerResult(
            marker_id="A1",
            category="A",
            name="Em-Dash Usage",
            count=count,
            score=score,
            max_contribution=150,
            evidence=evidence,
            description="Excessive em-dash usage can indicate AI-generated text.",
        )
    )
    marker_counts["A1_em_dash"] = count

    # A2 Colon/Semicolon Density
    matches = list(re.finditer(r"(?<![0-9])[:;](?![0-9/])", text))
    count = len(matches)
    density = (count / word_count) * 500 if word_count else 0
    excess = max(0.0, density - 1.0)
    score = excess * 10 * (word_count / 500) if word_count else 0
    evidence = build_snippets(text, matches)
    results.append(
        MarkerResult(
            marker_id="A2",
            category="A",
            name="Colon/Semicolon Density",
            count=count,
            score=score,
            max_contribution=100,
            evidence=evidence,
            description="Unusually high colon/semicolon density in running text.",
        )
    )
    marker_counts["A2_colon_semicolon"] = count

    # A3 Unicode Subscript/Superscript Characters
    matches = list(
        re.finditer(r"[₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ⁺⁻⁼⁽⁾]", text)
    )
    count = len(matches)
    score = count * 25
    evidence = build_snippets(text, matches)
    results.append(
        MarkerResult(
            marker_id="A3",
            category="A",
            name="Unicode Sub/Superscripts",
            count=count,
            score=score,
            max_contribution=150,
            evidence=evidence,
            description="Unicode sub/superscripts used instead of proper formatting.",
        )
    )
    marker_counts["A3_unicode_subscript"] = count

    # A4 Unusual Quotation Marks
    straight_total = len(QUOTE_STRAIGHT_RE.findall(text))
    smart_total = len(QUOTE_SMART_RE.findall(text))
    clusters = 0
    if straight_total and smart_total:
        for para in paragraphs:
            if QUOTE_STRAIGHT_RE.search(para) and QUOTE_SMART_RE.search(para):
                clusters += 1
    score = clusters * 5
    evidence = [
        {"text": p[:160], "index": i}
        for i, p in enumerate(paragraphs)
        if QUOTE_STRAIGHT_RE.search(p) and QUOTE_SMART_RE.search(p)
    ][:5]
    results.append(
        MarkerResult(
            marker_id="A4",
            category="A",
            name="Mixed Quotation Styles",
            count=clusters,
            score=score,
            max_contribution=50,
            evidence=evidence,
            description="Mixed straight and smart quotes in the same document.",
        )
    )
    marker_counts["A4_mixed_quotes"] = clusters

    return results


def detect_category_b(
    text: str, word_count: int, sentences: List[str], marker_counts: Dict
) -> List[MarkerResult]:
    results = []

    # B1 Transitional Word Patterns
    transitions = [
        "furthermore",
        "moreover",
        "additionally",
        "consequently",
        "subsequently",
        "nevertheless",
        "nonetheless",
        "correspondingly",
    ]
    count = 0
    evidence = []
    for idx, sent in enumerate(sentences):
        lower = sent.strip().lower()
        for word in transitions:
            if lower.startswith(f"{word},"):
                count += 1
                if len(evidence) < 5:
                    evidence.append({"text": sent[:160], "index": idx})
                break
    expected = (word_count / 1000) * 2 if word_count else 0
    excess = max(0.0, count - expected)
    score = excess * 8
    results.append(
        MarkerResult(
            marker_id="B1",
            category="B",
            name="Transitional Word Patterns",
            count=count,
            score=score,
            max_contribution=80,
            evidence=evidence,
            description="AI-style transitional phrases at sentence starts.",
        )
    )
    marker_counts["B1_transitional"] = count

    # B2 Enumeration Patterns
    enumeration_words = [
        "firstly",
        "first",
        "secondly",
        "second",
        "thirdly",
        "third",
        "fourthly",
        "fourth",
        "finally",
        "lastly",
    ]
    enum_flags = []
    enum_sentences = []
    for idx, sent in enumerate(sentences):
        lower = sent.strip().lower()
        for word in enumeration_words:
            if lower.startswith(f"{word},"):
                enum_flags.append(True)
                enum_sentences.append((idx, sent))
                break
        else:
            enum_flags.append(False)

    score = 0
    sequences = 0
    i = 0
    while i < len(enum_flags):
        if enum_flags[i]:
            start = i
            while i < len(enum_flags) and enum_flags[i]:
                i += 1
            length = i - start
            if length == 2:
                score += 6
                sequences += 1
            elif length >= 3:
                score += 12
                sequences += 1
        else:
            i += 1
    evidence = [{"text": sent[:160], "index": idx} for idx, sent in enum_sentences[:5]]
    results.append(
        MarkerResult(
            marker_id="B2",
            category="B",
            name="Enumeration Patterns",
            count=sequences,
            score=score,
            max_contribution=60,
            evidence=evidence,
            description="Firstly/Secondly/Finally enumeration sequences.",
        )
    )
    marker_counts["B2_enumeration"] = sequences

    # B3 Spacing Anomalies
    patterns = {
        r"\(\s+\S": "Space after opening parenthesis",
        r"\S\s+\)": "Space before closing parenthesis",
        r"\s—\s": "Spaces around em-dash",
        r"\d\s+–\s+\d": "Spaces around en-dash in ranges",
        r"\w\s+\/\s+\w": "Spaces around slash",
    }
    count = 0
    evidence = []
    for pattern in patterns:
        matches = list(re.finditer(pattern, text))
        count += len(matches)
        evidence.extend(build_snippets(text, matches, limit=2))
    score = count * 5
    results.append(
        MarkerResult(
            marker_id="B3",
            category="B",
            name="Spacing Anomalies",
            count=count,
            score=score,
            max_contribution=50,
            evidence=evidence[:5],
            description="Unusual spacing around punctuation or symbols.",
        )
    )
    marker_counts["B3_spacing"] = count

    # B4 Line Break Irregularities
    matches = list(re.finditer(r"[^\n]\n(?=[a-z])", text))
    count = len(matches)
    score = count * 3
    evidence = build_snippets(text, matches)
    results.append(
        MarkerResult(
            marker_id="B4",
            category="B",
            name="Line Break Irregularities",
            count=count,
            score=score,
            max_contribution=30,
            evidence=evidence,
            description="Unexpected mid-sentence line breaks.",
        )
    )
    marker_counts["B4_line_breaks"] = count

    # B5 Repetitive Sentence Structures
    score = 0
    clusters = 0
    evidence = []
    if POS_AVAILABLE and NLTK_AVAILABLE:
        pos_patterns = []
        for sent in sentences:
            try:
                tokens = word_tokenize(sent)
                tagged = pos_tag(tokens)
                # Extract POS tags, filtering out punctuation
                pos_tags = [tag for word, tag in tagged if tag not in ('.', ',', ':', ';', '!', '?')]
                if pos_tags:
                    pos_patterns.append(" ".join(pos_tags))
            except Exception:
                pos_patterns.append("")
        for i in range(len(pos_patterns) - 2):
            if pos_patterns[i] and pos_patterns[i+1] and pos_patterns[i+2]:
                sim1 = sequence_similarity(pos_patterns[i], pos_patterns[i + 1])
                sim2 = sequence_similarity(pos_patterns[i + 1], pos_patterns[i + 2])
                if sim1 >= 0.7 and sim2 >= 0.7:
                    clusters += 1
                    score += 10
                    if len(evidence) < 3:
                        evidence.append(
                            {
                                "text": " | ".join(
                                    s for s in sentences[i : i + 3]
                                )[:240],
                                "index": i,
                            }
                        )
    results.append(
        MarkerResult(
            marker_id="B5",
            category="B",
            name="Repetitive Sentence Structures",
            count=clusters,
            score=score,
            max_contribution=50,
            evidence=evidence,
            description="Consecutive sentences with highly similar structures.",
        )
    )
    marker_counts["B5_repetitive"] = clusters

    return results


def detect_category_c(
    text: str,
    word_count: int,
    doc_data: Dict,
    original_doc: Optional[Dict],
    marker_counts: Dict,
) -> List[MarkerResult]:
    results = []

    # C1 Extent of Edit (EoE)
    eoe = 0.0
    score = 0.0
    if original_doc is not None:
        original_words = WORD_RE.findall(original_doc.get("text") or "")
        edited_words = WORD_RE.findall(text)
        changed_words = calculate_changed_words(original_words, edited_words)
        eoe = (changed_words / word_count) * 100 if word_count else 0.0
        if eoe > 100:
            score = 30 + math.floor((eoe - 100) / 10) * 5
    results.append(
        MarkerResult(
            marker_id="C1",
            category="C",
            name="Extent of Edit",
            count=1 if eoe > 100 else 0,
            score=score,
            max_contribution=80,
            evidence=[{"text": f"EoE {eoe:.1f}%", "index": 0}] if eoe > 0 else [],
            description="Comparison of original vs edited extent of changes.",
        )
    )
    marker_counts["C1_eoe"] = eoe

    # C2 Large Text Chunk Detection
    insertions = [
        edit for edit in doc_data.get("track_changes", []) if edit.get("type") == "ins"
    ]
    large_chunks = [edit for edit in insertions if edit.get("word_count", 0) > 50]
    count = len(large_chunks)
    score = count * 20
    evidence = [
        {"text": edit.get("text", "")[:160], "index": edit.get("paragraph_index")}
        for edit in large_chunks[:5]
    ]
    results.append(
        MarkerResult(
            marker_id="C2",
            category="C",
            name="Large Inserted Chunks",
            count=count,
            score=score,
            max_contribution=100,
            evidence=evidence,
            description="Large inserted text blocks without granular edits.",
        )
    )
    marker_counts["C2_large_chunks"] = count

    # C3 Editing Time Analysis
    editing_minutes = doc_data.get("metadata", {}).get("editing_minutes")
    score = 0
    ratio = None
    if editing_minutes is not None and word_count:
        expected_hours = word_count / 1000
        actual_hours = editing_minutes / 60
        ratio = actual_hours / expected_hours if expected_hours else 0
        if ratio < 0.3:
            score = 30
        elif ratio < 0.5:
            score = 15
        elif ratio < 0.7:
            score = 5
    results.append(
        MarkerResult(
            marker_id="C3",
            category="C",
            name="Editing Time Analysis",
            count=1 if score > 0 else 0,
            score=score,
            max_contribution=30,
            evidence=[
                {"text": f"Edit time ratio {ratio:.2f}", "index": 0}
            ]
            if ratio is not None
            else [],
            description="Editing time compared to expected human editing speed.",
        )
    )
    marker_counts["C3_edit_time_ratio"] = ratio or 0

    # C4 Cluster Analysis
    edits = doc_data.get("track_changes", [])
    score = 0
    clustered = False
    if edits and doc_data.get("paragraphs"):
        segment_counts = [0] * 10
        total_paras = max(1, len(doc_data.get("paragraphs")))
        for edit in edits:
            idx = edit.get("paragraph_index")
            if idx is None:
                continue
            segment = min(9, int((idx / total_paras) * 10))
            segment_counts[segment] += 1
        total_edits = sum(segment_counts)
        if total_edits:
            top_two = sum(sorted(segment_counts, reverse=True)[:2])
            if top_two / total_edits > 0.6:
                clustered = True
                score = 15
    results.append(
        MarkerResult(
            marker_id="C4",
            category="C",
            name="Edit Cluster Analysis",
            count=1 if clustered else 0,
            score=score,
            max_contribution=15,
            evidence=[{"text": "Edits clustered in small document segments.", "index": 0}]
            if clustered
            else [],
            description="High concentration of edits in limited sections.",
        )
    )
    marker_counts["C4_clustered"] = 1 if clustered else 0

    return results


def detect_category_d(
    text: str, word_count: int, sentences: List[str], marker_counts: Dict
) -> List[MarkerResult]:
    results = []

    # D1 Hedging Language Overuse
    hedging_patterns = [
        r"It (is|should be) (important|worth|interesting) to (note|mention|observe) that",
        r"This (suggests|indicates|demonstrates) that",
    ]
    count = 0
    evidence = []
    for pattern in hedging_patterns:
        matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))
        count += len(matches)
        evidence.extend(build_snippets(text, matches, limit=2))
    expected = (word_count / 1000) * 2 if word_count else 0
    excess = max(0.0, count - expected)
    score = excess * 4
    results.append(
        MarkerResult(
            marker_id="D1",
            category="D",
            name="Hedging Language Overuse",
            count=count,
            score=score,
            max_contribution=40,
            evidence=evidence[:5],
            description="Overuse of hedging phrases.",
        )
    )
    marker_counts["D1_hedging_overuse"] = count

    # D2 Overly Formal Transitions
    formal_phrases = [
        "in light of the above",
        "taking into consideration",
        "with regard to",
        "in terms of",
        "it is evident that",
        "it can be observed that",
    ]
    count = 0
    evidence = []
    for phrase in formal_phrases:
        matches = list(re.finditer(re.escape(phrase), text, flags=re.IGNORECASE))
        count += len(matches)
        evidence.extend(build_snippets(text, matches, limit=2))
    score = count * 3
    results.append(
        MarkerResult(
            marker_id="D2",
            category="D",
            name="Overly Formal Transitions",
            count=count,
            score=score,
            max_contribution=30,
            evidence=evidence[:5],
            description="Formal transition phrases associated with AI writing.",
        )
    )
    marker_counts["D2_formal_transitions"] = count

    # D3 Passive Voice Density
    matches = list(
        re.finditer(
            r"\b(is|are|was|were|been|being)\s+\w+ed\b",
            text,
            flags=re.IGNORECASE,
        )
    )
    count = len(matches)
    passive_pct = (count / word_count) * 100 if word_count else 0
    score = passive_pct - 25 if passive_pct > 25 else 0
    evidence = build_snippets(text, matches)
    results.append(
        MarkerResult(
            marker_id="D3",
            category="D",
            name="Passive Voice Density",
            count=count,
            score=score,
            max_contribution=25,
            evidence=evidence,
            description="High passive voice density.",
        )
    )
    marker_counts["D3_passive_density"] = passive_pct

    # D4 Sentence Length Uniformity
    lengths = [len(WORD_RE.findall(s)) for s in sentences if WORD_RE.findall(s)]
    score = 0
    sd = 0
    if len(lengths) >= 2:
        sd = statistics.pstdev(lengths)
        if sd < 5:
            score = (5 - sd) * 10
    results.append(
        MarkerResult(
            marker_id="D4",
            category="D",
            name="Sentence Length Uniformity",
            count=1 if score > 0 else 0,
            score=score,
            max_contribution=30,
            evidence=[{"text": f"Sentence length SD {sd:.2f}", "index": 0}]
            if score > 0
            else [],
            description="Unusually uniform sentence lengths.",
        )
    )
    marker_counts["D4_sentence_uniformity"] = 1 if score > 0 else 0

    return results


def detect_category_e(
    text: str, paragraphs: List[str], marker_counts: Dict
) -> List[MarkerResult]:
    results = []

    # E1 AI-Favorite Words (expanded list)
    pattern = re.compile(
        r"\b(delve|delving|crucial|crucially|pivotal|multifaceted|nuanced|comprehensive|robust|leverage[sd]?|facilitate[sd]?|utilize[sd]?|landscape|paradigm|synergy|holistic|streamline[sd]?|foster[sd]?|underscores?|realm|encompasses?|intricate|notably|essentially|arguably|proliferation|unprecedented|simultaneously|inadvertently|perpetuate[sd]?|necessitat\w+|optimal|optimiz\w+|genuine|authentic|fundamental\w*|contemporary|methodolog\w+|empirical|demonstrate[sd]?|cohort|disparit\w+|discourse|evolve[sd]?|imperative[s]?|rigor)\b",
        flags=re.IGNORECASE,
    )
    matches = list(pattern.finditer(text))
    words = [m.group(0).lower() for m in matches]
    unique_words = set(words)
    unique_count = len(unique_words)
    score = 0
    if unique_count >= 9:
        score = 50
    elif unique_count >= 6:
        score = 30
    elif unique_count >= 3:
        score = 15
    if any(words.count(word) >= 3 for word in unique_words):
        score += 10
    evidence = build_snippets(text, matches)
    results.append(
        MarkerResult(
            marker_id="E1",
            category="E",
            name="AI-Favorite Words",
            count=unique_count,
            score=score,
            max_contribution=70,
            evidence=evidence,
            description="AI-favored vocabulary words detected.",
        )
    )
    marker_counts["E1_ai_words"] = unique_count

    # E2 Contraction Avoidance
    expanded_forms = [
        "do not",
        "does not",
        "did not",
        "cannot",
        "will not",
        "would not",
        "should not",
        "could not",
        "is not",
        "are not",
        "have not",
        "has not",
        "it is",
        "that is",
    ]
    contractions = [
        "don't",
        "doesn't",
        "didn't",
        "can't",
        "won't",
        "wouldn't",
        "shouldn't",
        "couldn't",
        "isn't",
        "aren't",
        "haven't",
        "hasn't",
        "it's",
        "that's",
    ]
    lower = text.lower()
    expanded_count = sum(
        len(re.findall(rf"\b{re.escape(term)}\b", lower)) for term in expanded_forms
    )
    contraction_count = sum(
        len(re.findall(rf"\b{re.escape(term)}\b", lower)) for term in contractions
    )
    total = expanded_count + contraction_count
    score = 0
    avoidance_ratio = 0
    if total > 5:
        avoidance_ratio = expanded_count / total
        if total > 10:
            if avoidance_ratio > 0.9:
                score = 25
            elif avoidance_ratio > 0.8:
                score = 15
            elif avoidance_ratio > 0.7:
                score = 5
    evidence = (
        [{"text": f"Avoidance ratio {avoidance_ratio:.2f}", "index": 0}] if total else []
    )
    results.append(
        MarkerResult(
            marker_id="E2",
            category="E",
            name="Contraction Avoidance",
            count=total,
            score=score,
            max_contribution=25,
            evidence=evidence,
            description="Preference for expanded forms over contractions.",
        )
    )
    marker_counts["E2_contraction_avoidance"] = avoidance_ratio

    # E3 Vocabulary Sophistication Uniformity
    avg_lengths = []
    for para in paragraphs:
        words = WORD_RE.findall(para)
        if not words:
            continue
        avg_lengths.append(sum(len(w) for w in words) / len(words))
    score = 0
    sd = 0
    if len(avg_lengths) >= 2:
        sd = statistics.pstdev(avg_lengths)
        if sd < 0.2:
            score = 20
        elif sd < 0.3:
            score = 10
    evidence = (
        [{"text": f"Avg word length SD {sd:.2f}", "index": 0}] if avg_lengths else []
    )
    results.append(
        MarkerResult(
            marker_id="E3",
            category="E",
            name="Vocabulary Sophistication Uniformity",
            count=1 if score > 0 else 0,
            score=score,
            max_contribution=20,
            evidence=evidence,
            description="Low variability in paragraph word-length averages.",
        )
    )
    marker_counts["E3_vocab_uniformity"] = 1 if score > 0 else 0

    return results


def detect_category_f(
    text: str, paragraphs: List[str], sentences: List[str], marker_counts: Dict
) -> List[MarkerResult]:
    results = []

    # F1 Paragraph Length Uniformity
    para_lengths = [len(WORD_RE.findall(p)) for p in paragraphs if WORD_RE.findall(p)]
    score = 0
    cv = 0
    if len(para_lengths) >= 2:
        mean = statistics.mean(para_lengths)
        sd = statistics.pstdev(para_lengths)
        cv = sd / mean if mean else 0
        if cv < 0.15:
            score = 25
        elif cv < 0.25:
            score = 15
        elif cv < 0.35:
            score = 5
    evidence = (
        [{"text": f"Paragraph length CV {cv:.2f}", "index": 0}] if para_lengths else []
    )
    results.append(
        MarkerResult(
            marker_id="F1",
            category="F",
            name="Paragraph Length Uniformity",
            count=1 if score > 0 else 0,
            score=score,
            max_contribution=25,
            evidence=evidence,
            description="Paragraph lengths show unusually low variance.",
        )
    )
    marker_counts["F1_para_uniformity"] = 1 if score > 0 else 0

    # F2 Perfect Parallel Structures
    score = 0
    sets = 0
    evidence = []
    patterns = []
    for sent in sentences:
        tokens = [t for t in WORD_RE.findall(sent.lower())][:3]
        if tokens:
            patterns.append(" ".join(tokens))
        else:
            patterns.append("")
    i = 0
    while i < len(patterns):
        if patterns[i]:
            start = i
            while i < len(patterns) and patterns[i] == patterns[start]:
                i += 1
            length = i - start
            if length >= 4:
                sets += 1
                score += 10
                if len(evidence) < 3:
                    evidence.append(
                        {
                            "text": " | ".join(sentences[start:i])[:240],
                            "index": start,
                        }
                    )
        else:
            i += 1
    results.append(
        MarkerResult(
            marker_id="F2",
            category="F",
            name="Perfect Parallel Structures",
            count=sets,
            score=score,
            max_contribution=30,
            evidence=evidence,
            description="Multiple list items with identical structure.",
        )
    )
    marker_counts["F2_parallel_structures"] = sets

    # F3 Balanced Argument Pattern
    pros_count, cons_count = find_balanced_sections(text)
    score = 0
    if pros_count >= 4 and pros_count == cons_count:
        score = 15
    evidence = []
    if score:
        evidence.append({"text": f"Pros {pros_count} vs Cons {cons_count}", "index": 0})
    results.append(
        MarkerResult(
            marker_id="F3",
            category="F",
            name="Balanced Argument Pattern",
            count=1 if score > 0 else 0,
            score=score,
            max_contribution=15,
            evidence=evidence,
            description="Pros and cons lists perfectly balanced.",
        )
    )
    marker_counts["F3_balanced_argument"] = 1 if score > 0 else 0

    return results


def detect_category_g(
    text: str, sentences: List[str], marker_counts: Dict
) -> List[MarkerResult]:
    results = []

    # G1 Lack of Specific Examples
    vague_terms = [
        "many studies show",
        "research indicates",
        "experts agree",
        "some researchers",
        "various factors",
        "numerous examples",
        "several aspects",
    ]
    vague_count = sum(
        len(re.findall(re.escape(term), text, flags=re.IGNORECASE)) for term in vague_terms
    )
    if POS_AVAILABLE and NLTK_AVAILABLE:
        try:
            tokens = word_tokenize(text)
            tagged = pos_tag(tokens)
            # Count proper nouns (NNP, NNPS) and numbers (CD)
            specific_items = sum(1 for word, tag in tagged if tag in ('NNP', 'NNPS', 'CD'))
        except Exception:
            specific_items = len(re.findall(r"\b[A-Z][a-z]+\b", text)) + len(re.findall(r"\d+", text))
    else:
        specific_items = len(re.findall(r"\b[A-Z][a-z]+\b", text)) + len(
            re.findall(r"\d+", text)
        )
    ratio = vague_count / (specific_items + 1)
    score = 0
    if ratio > 3.0:
        score = 25
    elif ratio > 2.0:
        score = 15
    elif ratio > 1.0:
        score = 5
    evidence = (
        [{"text": f"Vague/specific ratio {ratio:.2f}", "index": 0}] if vague_count else []
    )
    results.append(
        MarkerResult(
            marker_id="G1",
            category="G",
            name="Lack of Specific Examples",
            count=vague_count,
            score=score,
            max_contribution=25,
            evidence=evidence,
            description="High ratio of vague quantifiers to specific details.",
        )
    )
    marker_counts["G1_lack_specifics"] = ratio

    # G2 Circular Definitions
    matches = []
    for sent in sentences:
        match = re.search(
            r"\b(\w+)\b\s+(is defined as|refers to|means)\s+([^\.]+)",
            sent,
            flags=re.IGNORECASE,
        )
        if match:
            subject = match.group(1).lower()
            definition = match.group(3).lower()
            if subject in definition:
                matches.append(sent)
    count = len(matches)
    score = count * 15
    evidence = [{"text": sent[:160], "index": idx} for idx, sent in enumerate(matches[:5])]
    results.append(
        MarkerResult(
            marker_id="G2",
            category="G",
            name="Circular Definitions",
            count=count,
            score=score,
            max_contribution=30,
            evidence=evidence,
            description="Definitions that reuse the term being defined.",
        )
    )
    marker_counts["G2_circular_definitions"] = count

    # G3 Generic Statements Without Substance
    generic_patterns = [
        r"\b\w+ is important\b",
        r"\b\w+ plays a crucial role\b",
        r"\b\w+ has both advantages and disadvantages\b",
        r"\b\w+ is a complex topic\b",
        r"\b\w+ requires careful consideration\b",
        r"\b\w+ is essential for success\b",
        r"\b\w+ has become increasingly important\b",
    ]
    count = 0
    evidence = []
    for pattern in generic_patterns:
        matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))
        count += len(matches)
        evidence.extend(build_snippets(text, matches, limit=2))
    score = count * 3
    results.append(
        MarkerResult(
            marker_id="G3",
            category="G",
            name="Generic Statements",
            count=count,
            score=score,
            max_contribution=30,
            evidence=evidence[:5],
            description="Generic statements that lack concrete substance.",
        )
    )
    marker_counts["G3_generic_statements"] = count

    return results


def detect_category_h(doc_data: Dict, word_count: int, marker_counts: Dict) -> List[MarkerResult]:
    results = []
    text = doc_data.get("text") or ""

    # H1 Font Inconsistencies
    font_info = doc_data.get("font_info", {})
    clusters = font_info.get("clusters", 0)
    score = clusters * 10
    results.append(
        MarkerResult(
            marker_id="H1",
            category="H",
            name="Font Inconsistencies",
            count=clusters,
            score=score,
            max_contribution=40,
            evidence=[{"text": f"Font change clusters: {clusters}", "index": 0}]
            if clusters
            else [],
            description="Abrupt font changes in the document.",
        )
    )
    marker_counts["H1_font_inconsistent"] = clusters

    # H2 Style Inconsistencies
    style_info = doc_data.get("style_info", {})
    inconsistencies = 0
    evidence = []
    if len(style_info.get("heading_styles", [])) > 1:
        inconsistencies += 1
        evidence.append({"text": "Multiple heading styles detected.", "index": 0})
    if len(style_info.get("list_styles", [])) > 1:
        inconsistencies += 1
        evidence.append({"text": "Multiple list styles detected.", "index": 0})
    if len(style_info.get("spacing_values", [])) > 1:
        inconsistencies += 1
        evidence.append({"text": "Paragraph spacing inconsistencies detected.", "index": 0})
    score = inconsistencies * 5
    results.append(
        MarkerResult(
            marker_id="H2",
            category="H",
            name="Style Inconsistencies",
            count=inconsistencies,
            score=score,
            max_contribution=25,
            evidence=evidence[:5],
            description="Mixed heading, list, or spacing styles.",
        )
    )
    marker_counts["H2_style_inconsistent"] = inconsistencies

    # H3 Metadata Timestamp Anomalies
    metadata = doc_data.get("metadata", {})
    revision = metadata.get("revision")
    created = metadata.get("created")
    modified = metadata.get("modified")
    anomalies = 0
    score = 0
    evidence = []
    if word_count > 5000 and isinstance(revision, int) and revision < 3:
        anomalies += 1
        score += 20
        evidence.append(
            {"text": f"Low revision count ({revision}) for large doc.", "index": 0}
        )
    if created and modified and modified < created + timedelta(minutes=10) and word_count > 5000:
        anomalies += 1
        score += 15
        evidence.append({"text": "Modification time close to creation time.", "index": 0})
    results.append(
        MarkerResult(
            marker_id="H3",
            category="H",
            name="Metadata Timestamp Anomalies",
            count=anomalies,
            score=score,
            max_contribution=25,
            evidence=evidence[:5],
            description="Suspicious metadata timing for large documents.",
        )
    )
    marker_counts["H3_metadata_anomalies"] = anomalies

    # H5 Clipboard Artifacts
    matches = list(re.finditer(r"[\u200B\u200C\u200D\uFEFF\u00A0\uFFFC]", text))
    clusters = 0
    last_pos = None
    for match in matches:
        if last_pos is None or match.start() - last_pos > 5:
            clusters += 1
        last_pos = match.start()
    score = clusters * 10
    evidence = build_snippets(text, matches)
    results.append(
        MarkerResult(
            marker_id="H5",
            category="H",
            name="Clipboard Artifacts",
            count=clusters,
            score=score,
            max_contribution=40,
            evidence=evidence,
            description="Unusual whitespace or hidden characters from copy-paste.",
        )
    )
    marker_counts["H5_clipboard_artifacts"] = clusters

    return results


def detect_category_i(
    text: str, paragraphs: List[str], sentences: List[str], marker_counts: Dict
) -> List[MarkerResult]:
    results = []

    # I1 Citation Anomalies
    author_year = re.findall(r"\([A-Z][A-Za-z]+,?\s+\d{4}\)", text)
    numeric = re.findall(r"\[\d+\]", text)
    et_al = re.findall(r"\bet al\.\b", text, flags=re.IGNORECASE)
    round_years = re.findall(r"\b(2020|2021|2022)\b", text)
    clusters = 0
    evidence = []
    if author_year and numeric:
        clusters += 1
        evidence.append({"text": "Mixed citation styles detected.", "index": 0})
    if len(round_years) >= 3:
        clusters += 1
        evidence.append({"text": f"Round-year citations: {len(round_years)}", "index": 0})
    if len(et_al) >= 3:
        clusters += 1
        evidence.append({"text": f"Et al. usage: {len(et_al)}", "index": 0})
    score = clusters * 15
    results.append(
        MarkerResult(
            marker_id="I1",
            category="I",
            name="Citation Anomalies",
            count=clusters,
            score=score,
            max_contribution=45,
            evidence=evidence[:5],
            description="Suspicious or inconsistent citation patterns.",
        )
    )
    marker_counts["I1_citation_anomalies"] = clusters

    # I2 Generic Methodology Descriptions
    methodology_markers = [
        "standard procedures were followed",
        "appropriate statistical methods",
        "conventional techniques",
        "established protocols",
    ]
    count = sum(
        len(re.findall(re.escape(m), text, flags=re.IGNORECASE)) for m in methodology_markers
    )
    score = 0
    if count >= 4:
        score = 20
    elif count >= 2:
        score = 10
    evidence = [
        {"text": m, "index": 0}
        for m in methodology_markers
        if re.search(re.escape(m), text, flags=re.IGNORECASE)
    ]
    results.append(
        MarkerResult(
            marker_id="I2",
            category="I",
            name="Generic Methodology",
            count=count,
            score=score,
            max_contribution=20,
            evidence=evidence[:5],
            description="Vague methodology language without specific details.",
        )
    )
    marker_counts["I2_generic_method"] = count

    # I3 Results Without Data
    score = 0
    found_results = None
    results_section = []
    for idx, para in enumerate(paragraphs):
        if re.match(r"^\s*(results|findings)\b", para, flags=re.IGNORECASE):
            found_results = idx
            break
    if found_results is not None:
        results_section = paragraphs[found_results : found_results + 5]
        section_text = " ".join(results_section)
        has_numbers = bool(re.search(r"\d", section_text))
        qualitative_markers = [
            "showed significant improvement",
            "demonstrated positive results",
            "indicated a trend",
        ]
        if not has_numbers and any(
            re.search(re.escape(m), section_text, flags=re.IGNORECASE)
            for m in qualitative_markers
        ):
            score = 15
    evidence = [{"text": p[:160], "index": found_results}] if score and results_section else []
    results.append(
        MarkerResult(
            marker_id="I3",
            category="I",
            name="Results Without Data",
            count=1 if score > 0 else 0,
            score=score,
            max_contribution=15,
            evidence=evidence,
            description="Results described qualitatively without quantitative data.",
        )
    )
    marker_counts["I3_results_no_data"] = 1 if score > 0 else 0

    return results


def detect_category_j(doc_data: Dict, paragraphs: List[str], marker_counts: Dict) -> List[MarkerResult]:
    results = []
    edits = doc_data.get("track_changes", [])
    total_paras = max(1, len(paragraphs))

    # J1 Wholesale Replacement Pattern
    rewritten_paras = 0
    if edits:
        para_word_counts = [len(WORD_RE.findall(p)) for p in paragraphs]
        edits_by_para = {}
        for edit in edits:
            idx = edit.get("paragraph_index")
            if idx is None:
                continue
            edits_by_para.setdefault(idx, 0)
            edits_by_para[idx] += edit.get("word_count", 0)
        for idx, edit_words in edits_by_para.items():
            total_words = para_word_counts[idx] if idx < len(para_word_counts) else 0
            if total_words and edit_words / total_words > 0.5:
                rewritten_paras += 1
    rewrite_ratio = rewritten_paras / total_paras
    score = 0
    if rewrite_ratio > 0.8:
        score = 35
    elif rewrite_ratio > 0.6:
        score = 20
    elif rewrite_ratio > 0.4:
        score = 10
    results.append(
        MarkerResult(
            marker_id="J1",
            category="J",
            name="Wholesale Replacement Pattern",
            count=rewritten_paras,
            score=score,
            max_contribution=35,
            evidence=[{"text": f"Rewrite ratio {rewrite_ratio:.2f}", "index": 0}]
            if edits
            else [],
            description="Large percentage of paragraphs rewritten.",
        )
    )
    marker_counts["J1_wholesale"] = rewritten_paras

    # J2 Edit Granularity Analysis
    sentence_level = 0
    total_edits = 0
    for edit in edits:
        size = edit.get("word_count", 0)
        if size == 0:
            continue
        total_edits += 1
        if size >= 20:
            sentence_level += 1
    ratio = sentence_level / total_edits if total_edits else 0
    score = 0
    if ratio > 0.7:
        score = 25
    elif ratio > 0.5:
        score = 15
    results.append(
        MarkerResult(
            marker_id="J2",
            category="J",
            name="Edit Granularity",
            count=sentence_level,
            score=score,
            max_contribution=25,
            evidence=[{"text": f"Sentence-level edit ratio {ratio:.2f}", "index": 0}]
            if edits
            else [],
            description="High ratio of sentence-level edits vs word-level edits.",
        )
    )
    marker_counts["J2_edit_granularity"] = ratio

    return results


def calculate_weighted_score(category_scores: Dict[str, float]) -> (float, float):
    weighted = sum(
        category_scores[cat] * CATEGORY_WEIGHTS[cat] for cat in CATEGORY_WEIGHTS
    )
    max_weighted = sum(CATEGORY_CAPS[cat] * CATEGORY_WEIGHTS[cat] for cat in CATEGORY_WEIGHTS)
    return weighted, max_weighted


def adjust_for_confidence(final_score: float, document_length: int, markers_found: int) -> Dict:
    if document_length < 500:
        confidence_factor = 0.7
    elif document_length < 1000:
        confidence_factor = 0.85
    else:
        confidence_factor = 1.0

    if markers_found < 3 and final_score > 50:
        final_score *= 0.8

    adjusted_score = final_score * confidence_factor
    return {
        "score": round(final_score, 1),
        "confidence": confidence_factor,
        "adjusted_score": round(adjusted_score, 1),
    }


def classify_risk(score: float, high_confidence_markers: int) -> str:
    if score <= 15:
        classification = "MINIMAL"
    elif score <= 35:
        classification = "LOW"
    elif score <= 55:
        classification = "MODERATE"
    elif score <= 75:
        classification = "HIGH"
    else:
        classification = "CRITICAL"

    if high_confidence_markers >= 3 and classification in ["MINIMAL", "LOW"]:
        classification = "MODERATE"
    if high_confidence_markers >= 5 and classification == "MODERATE":
        classification = "HIGH"

    return classification


def apply_composite_override(classification: str, composites: List[Dict]) -> str:
    if not composites:
        return classification
    order = ["MINIMAL", "LOW", "MODERATE", "HIGH", "CRITICAL"]
    current_index = order.index(classification)
    for comp in composites:
        auto = comp.get("auto_classify")
        if auto in order:
            current_index = max(current_index, order.index(auto))
    return order[current_index]


def confidence_level(confidence_factor: float) -> str:
    if confidence_factor >= 0.9:
        return "HIGH"
    if confidence_factor >= 0.75:
        return "MEDIUM"
    return "LOW"


def recommendation_for_classification(classification: str) -> str:
    if classification in ["MINIMAL", "LOW"]:
        return "Low probability of AI use. No action needed; monitor only and document evidence."
    if classification == "MODERATE":
        return "Medium probability of AI use. Manual review recommended; investigate and offer re-edit if needed."
    if classification == "HIGH":
        return "High probability of AI use. Investigation required with remediation planning."
    return "Critical probability of AI use. Immediate escalation and remediation required."


def detect_human_indicators(
    text: str,
    sentences: List[str],
    word_count: int,
    doc_data: Dict,
) -> (List[Dict], float):
    indicators = []
    reduction = 0.0

    # TYPO_PATTERN (Track Changes)
    edits = doc_data.get("track_changes", [])
    if edits:
        small_edits = sum(1 for edit in edits if 0 < edit.get("word_count", 0) <= 2)
        if small_edits >= 10:
            indicators.append(
                {
                    "id": "TYPO_PATTERN",
                    "description": "Presence of frequent small corrections.",
                    "score_reduction": 15,
                    "rationale": "Small typo-like edits suggest human revision.",
                }
            )
            reduction += 15

    # INCONSISTENT_STYLE
    lengths = [len(WORD_RE.findall(s)) for s in sentences if WORD_RE.findall(s)]
    if len(lengths) >= 2:
        sd = statistics.pstdev(lengths)
        if sd > 12:
            indicators.append(
                {
                    "id": "INCONSISTENT_STYLE",
                    "description": "High variance in sentence lengths.",
                    "score_reduction": 10,
                    "rationale": "Natural variation suggests human writing.",
                }
            )
            reduction += 10

    # PERSONAL_VOICE
    personal_count = len(
        re.findall(r"\b(I|we|my|our|me|us)\b", text, flags=re.IGNORECASE)
    )
    if personal_count >= 5:
        indicators.append(
            {
                "id": "PERSONAL_VOICE",
                "description": "First-person perspective detected.",
                "score_reduction": 20,
                "rationale": "Personal voice is less typical of AI output.",
            }
        )
        reduction += 20

    # DOMAIN_EXPERTISE
    if POS_AVAILABLE and NLTK_AVAILABLE:
        try:
            tokens = word_tokenize(text)
            tagged = pos_tag(tokens)
            propn_count = sum(1 for word, tag in tagged if tag in ('NNP', 'NNPS'))
            num_count = sum(1 for word, tag in tagged if tag == 'CD')
        except Exception:
            propn_count = len(re.findall(r"\b[A-Z][a-z]+\b", text))
            num_count = len(re.findall(r"\d+", text))
    else:
        propn_count = len(re.findall(r"\b[A-Z][a-z]+\b", text))
        num_count = len(re.findall(r"\d+", text))
    detail_ratio = (propn_count + num_count) / word_count if word_count else 0
    if detail_ratio > 0.08:
        indicators.append(
            {
                "id": "DOMAIN_EXPERTISE",
                "description": "High density of specific names or numbers.",
                "score_reduction": 15,
                "rationale": "Specific domain details suggest human expertise.",
            }
        )
        reduction += 15

    # COLLOQUIALISMS
    contraction_count = len(re.findall(r"\b\w+'[a-z]+\b", text))
    if word_count and contraction_count / word_count > 0.02:
        indicators.append(
            {
                "id": "COLLOQUIALISMS",
                "description": "Frequent contractions and informal phrasing.",
                "score_reduction": 10,
                "rationale": "Colloquial tone suggests human writing.",
            }
        )
        reduction += 10

    return indicators, reduction


def build_snippets(
    text: str, matches: List[re.Match], window: int = 40, limit: int = 5
) -> List[Dict]:
    snippets = []
    for match in matches[:limit]:
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        snippet = text[start:end].replace("\n", " ").strip()
        snippets.append({"text": snippet, "index": match.start()})
    return snippets


def sequence_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    matcher = SequenceMatcher(None, a, b)
    return matcher.ratio()


def calculate_changed_words(original_words: List[str], edited_words: List[str]) -> int:
    matcher = SequenceMatcher(None, original_words, edited_words)
    changed = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ("replace", "delete", "insert"):
            changed += max(i2 - i1, j2 - j1)
    return changed


def detect_document_type(text: str) -> str:
    academic_signals = [
        "abstract",
        "introduction",
        "methodology",
        "results",
        "discussion",
        "conclusion",
        "references",
        "et al.",
        "p-value",
        "hypothesis",
        "statistical",
    ]
    business_signals = [
        "executive summary",
        "stakeholder",
        "roi",
        "kpi",
        "deliverable",
        "milestone",
        "quarterly",
    ]
    lower = text.lower()
    academic_score = sum(1 for s in academic_signals if s in lower)
    business_score = sum(1 for s in business_signals if s in lower)
    if academic_score > 5:
        return "academic"
    if business_score > 3:
        return "business"
    return "general"


def find_balanced_sections(text: str) -> (int, int):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    pros_count = 0
    cons_count = 0
    current = None
    for line in lines:
        header = line.lower()
        if header.startswith("pros") or header.startswith("advantages") or header.startswith(
            "benefits"
        ):
            current = "pros"
            continue
        if header.startswith("cons") or header.startswith("disadvantages") or header.startswith(
            "limitations"
        ):
            current = "cons"
            continue
        if line.startswith("-") or line.startswith("•") or re.match(r"^\d+\.", line):
            if current == "pros":
                pros_count += 1
            elif current == "cons":
                cons_count += 1
    return pros_count, cons_count


def check_composite_patterns(marker_counts: Dict) -> List[Dict]:
    composite_patterns = {
        "SMOKING_GUN_1": {
            "name": "Copy-Paste Signature",
            "required_markers": [
                "A1_em_dash >= 5",
                "H5_clipboard_artifacts",
                "J4_time_gap",
            ],
            "bonus_score": 50,
            "auto_classify": "HIGH",
            "description": "Multiple em-dashes + clipboard artifacts + suspicious timing",
        },
        "SMOKING_GUN_2": {
            "name": "AI Writing Style Bundle",
            "required_markers": [
                "E1_ai_words >= 5",
                "B1_transitional >= 4",
                "F1_para_uniformity",
            ],
            "bonus_score": 40,
            "auto_classify": "HIGH",
            "description": "AI vocabulary + transitional patterns + uniform structure",
        },
        "SMOKING_GUN_3": {
            "name": "Wholesale Replacement Evidence",
            "required_markers": ["C1_eoe > 100", "C2_large_chunks >= 2", "J1_wholesale"],
            "bonus_score": 60,
            "auto_classify": "CRITICAL",
            "description": "High EoE + large chunk insertions + wholesale edit pattern",
        },
        "SUSPICIOUS_COMBO_1": {
            "name": "Academic AI Pattern",
            "required_markers": [
                "G1_lack_specifics",
                "I2_generic_method >= 2",
                "D1_hedging_overuse >= 2",
            ],
            "bonus_score": 25,
            "auto_classify": "MODERATE",
            "description": "Vague content + generic methodology + excessive hedging",
        },
        "SUSPICIOUS_COMBO_2": {
            "name": "Format Inconsistency Bundle",
            "required_markers": [
                "H1_font_inconsistent",
                "H2_style_inconsistent",
                "H5_clipboard_artifacts",
            ],
            "bonus_score": 30,
            "auto_classify": "MODERATE",
            "description": "Multiple formatting artifacts suggesting external paste",
        },
    }

    triggered = []
    for pattern_id, pattern in composite_patterns.items():
        if all(evaluate_condition(cond, marker_counts) for cond in pattern["required_markers"]):
            triggered.append(
                {
                    "pattern": pattern_id,
                    "name": pattern["name"],
                    "bonus": pattern["bonus_score"],
                    "auto_classify": pattern["auto_classify"],
                    "description": pattern["description"],
                }
            )
    return triggered


def evaluate_condition(condition: str, marker_counts: Dict) -> bool:
    parts = condition.split()
    if len(parts) == 1:
        return marker_counts.get(parts[0], 0) not in (0, False, None)
    if len(parts) == 3:
        key, op, value = parts
        try:
            target = float(value.replace("%", ""))
        except ValueError:
            return False
        current = marker_counts.get(key, 0)
        if op == ">=":
            return current >= target
        if op == ">":
            return current > target
        if op == "<=":
            return current <= target
        if op == "==":
            return current == target
    return False
