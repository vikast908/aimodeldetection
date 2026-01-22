"""
Advanced features for enhanced AI detection accuracy.
This module adds sophisticated statistical and ML-ready features.
"""

import math
import re
import statistics
from collections import Counter
from typing import Dict, List, Tuple, Optional

from .parsers import WORD_RE


def calculate_lexical_diversity(text: str) -> Dict[str, float]:
    """
    Calculate multiple lexical diversity metrics.
    AI text tends to have lower lexical diversity.
    """
    words = WORD_RE.findall(text.lower())
    if not words:
        return {
            "type_token_ratio": 0.0,
            "yule_k": 0.0,
            "simpson_index": 0.0,
            "hapax_legomena_ratio": 0.0,
            "mtld": 0.0,
        }

    unique_words = set(words)
    word_freq = Counter(words)
    total_words = len(words)
    unique_count = len(unique_words)

    # Type-Token Ratio (TTR)
    ttr = unique_count / total_words if total_words else 0

    # Yule's K (lower = more diverse)
    if total_words > 0:
        m1 = total_words
        m2 = sum(freq ** 2 for freq in word_freq.values())
        yule_k = 10000 * (m2 - m1) / (m1 ** 2) if m1 > 0 else 0
    else:
        yule_k = 0

    # Simpson's Index (higher = more diverse)
    if total_words > 1:
        simpson = 1 - sum((freq / total_words) ** 2 for freq in word_freq.values())
    else:
        simpson = 0

    # Hapax Legomena Ratio (words appearing once)
    hapax_count = sum(1 for freq in word_freq.values() if freq == 1)
    hapax_ratio = hapax_count / unique_count if unique_count else 0

    # MTLD (Measure of Textual Lexical Diversity)
    mtld = calculate_mtld(words)

    return {
        "type_token_ratio": round(ttr, 4),
        "yule_k": round(yule_k, 2),
        "simpson_index": round(simpson, 4),
        "hapax_legomena_ratio": round(hapax_ratio, 4),
        "mtld": round(mtld, 2),
    }


def calculate_mtld(words: List[str], threshold: float = 0.72) -> float:
    """
    Calculate Measure of Textual Lexical Diversity.
    Higher values indicate greater lexical diversity.
    """
    if len(words) < 50:
        return 0.0

    def mtld_forward(word_list: List[str]) -> float:
        ttr = 1.0
        token_count = 0
        type_count = 0
        types = set()
        factor_count = 0

        for word in word_list:
            token_count += 1
            if word not in types:
                type_count += 1
                types.add(word)
            ttr = type_count / token_count

            if ttr <= threshold:
                factor_count += 1
                token_count = 0
                type_count = 0
                types = set()

        if token_count > 0:
            factor_count += (1 - ttr) / (1 - threshold)

        return len(word_list) / factor_count if factor_count > 0 else len(word_list)

    forward_mtld = mtld_forward(words)
    backward_mtld = mtld_forward(words[::-1])

    return (forward_mtld + backward_mtld) / 2


def calculate_readability_scores(text: str, sentences: List[str]) -> Dict[str, float]:
    """
    Calculate multiple readability metrics.
    AI text often has consistent readability scores.
    """
    words = WORD_RE.findall(text)
    if not words or not sentences:
        return {
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "gunning_fog": 0.0,
            "smog_index": 0.0,
            "coleman_liau_index": 0.0,
            "ari": 0.0,
        }

    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(count_syllables(word) for word in words)
    complex_words = sum(1 for word in words if count_syllables(word) >= 3)
    characters = sum(len(word) for word in words)

    # Flesch Reading Ease
    avg_sentence_length = total_words / total_sentences if total_sentences else 0
    avg_syllables_per_word = total_syllables / total_words if total_words else 0
    flesch_reading_ease = (
        206.835
        - 1.015 * avg_sentence_length
        - 84.6 * avg_syllables_per_word
    )

    # Flesch-Kincaid Grade Level
    flesch_kincaid_grade = (
        0.39 * avg_sentence_length
        + 11.8 * avg_syllables_per_word
        - 15.59
    )

    # Gunning Fog Index
    percent_complex = (complex_words / total_words * 100) if total_words else 0
    gunning_fog = 0.4 * (avg_sentence_length + percent_complex)

    # SMOG Index
    if total_sentences >= 30:
        smog = 1.0430 * math.sqrt(complex_words * (30 / total_sentences)) + 3.1291
    else:
        smog = 0.0

    # Coleman-Liau Index
    L = (characters / total_words * 100) if total_words else 0
    S = (total_sentences / total_words * 100) if total_words else 0
    coleman_liau = 0.0588 * L - 0.296 * S - 15.8

    # Automated Readability Index (ARI)
    ari = (
        4.71 * (characters / total_words)
        + 0.5 * (total_words / total_sentences)
        - 21.43
        if total_words and total_sentences
        else 0
    )

    return {
        "flesch_reading_ease": round(flesch_reading_ease, 2),
        "flesch_kincaid_grade": round(max(0, flesch_kincaid_grade), 2),
        "gunning_fog": round(gunning_fog, 2),
        "smog_index": round(smog, 2),
        "coleman_liau_index": round(coleman_liau, 2),
        "ari": round(ari, 2),
    }


def count_syllables(word: str) -> int:
    """
    Estimate syllable count for a word.
    """
    word = word.lower()
    vowels = "aeiouy"
    syllable_count = 0
    previous_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel

    # Adjust for silent e
    if word.endswith("e"):
        syllable_count -= 1

    # Ensure at least one syllable
    return max(1, syllable_count)


def calculate_ngram_repetition(text: str, n: int = 3) -> Dict[str, any]:
    """
    Detect repetitive n-gram patterns.
    AI text often has repeated phrases.
    """
    words = WORD_RE.findall(text.lower())
    if len(words) < n:
        return {"repetition_score": 0.0, "repeated_ngrams": [], "max_repetitions": 0}

    ngrams = []
    for i in range(len(words) - n + 1):
        ngram = " ".join(words[i:i + n])
        ngrams.append(ngram)

    ngram_freq = Counter(ngrams)
    repeated = {ng: count for ng, count in ngram_freq.items() if count > 1}

    if not repeated:
        return {"repetition_score": 0.0, "repeated_ngrams": [], "max_repetitions": 0}

    max_reps = max(repeated.values())
    total_ngrams = len(ngrams)
    repeated_count = sum(repeated.values())
    repetition_score = (repeated_count / total_ngrams * 100) if total_ngrams else 0

    # Get top repeated n-grams
    top_repeated = sorted(repeated.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "repetition_score": round(repetition_score, 2),
        "repeated_ngrams": [{"ngram": ng, "count": c} for ng, c in top_repeated],
        "max_repetitions": max_reps,
    }


def calculate_burstiness(sentences: List[str]) -> Dict[str, float]:
    """
    Calculate burstiness - variation in sentence complexity.
    Human writing has higher burstiness; AI text is more uniform.
    """
    if len(sentences) < 2:
        return {
            "burstiness_score": 0.0,
            "perplexity_variance": 0.0,
            "complexity_variation": 0.0,
        }

    sentence_lengths = [len(WORD_RE.findall(s)) for s in sentences]
    sentence_complexities = []

    for sent in sentences:
        words = WORD_RE.findall(sent)
        if words:
            avg_word_length = sum(len(w) for w in words) / len(words)
            comma_count = sent.count(",")
            conjunction_count = len(re.findall(r"\b(and|but|or|while|because|if|when|although)\b", sent.lower()))
            complexity = avg_word_length + (comma_count * 2) + (conjunction_count * 1.5)
            sentence_complexities.append(complexity)
        else:
            sentence_complexities.append(0)

    # Burstiness = std_dev / mean (coefficient of variation)
    if sentence_lengths:
        mean_length = statistics.mean(sentence_lengths)
        std_length = statistics.pstdev(sentence_lengths)
        burstiness = (std_length / mean_length) if mean_length > 0 else 0
    else:
        burstiness = 0

    # Complexity variation
    if len(sentence_complexities) >= 2:
        complexity_var = statistics.pstdev(sentence_complexities)
    else:
        complexity_var = 0

    # Calculate local variance (perplexity proxy)
    local_variances = []
    window_size = 3
    for i in range(len(sentence_lengths) - window_size + 1):
        window = sentence_lengths[i:i + window_size]
        if len(window) >= 2:
            local_var = statistics.pstdev(window)
            local_variances.append(local_var)

    perplexity_var = statistics.mean(local_variances) if local_variances else 0

    return {
        "burstiness_score": round(burstiness, 4),
        "perplexity_variance": round(perplexity_var, 2),
        "complexity_variation": round(complexity_var, 2),
    }


def bayesian_score_adjustment(
    base_score: float,
    marker_counts: Dict[str, float],
    document_type: str,
    word_count: int
) -> Dict[str, float]:
    """
    Apply Bayesian reasoning to adjust scores based on prior probabilities
    and evidence strength.
    """
    # Prior probabilities based on document type
    priors = {
        "academic": 0.15,  # 15% of academic docs might be AI-assisted
        "business": 0.25,  # 25% of business docs might be AI-assisted
        "general": 0.30,   # 30% of general docs might be AI-assisted
    }

    prior = priors.get(document_type, 0.25)

    # Calculate likelihood ratio based on evidence strength
    high_confidence_markers = sum(
        1 for key, val in marker_counts.items()
        if key.startswith("A") and val > 0
    )

    # Likelihood of observing this evidence given AI (P(E|AI))
    if high_confidence_markers >= 5:
        likelihood_ai = 0.95
    elif high_confidence_markers >= 3:
        likelihood_ai = 0.80
    elif high_confidence_markers >= 1:
        likelihood_ai = 0.60
    else:
        likelihood_ai = 0.30

    # Likelihood of observing this evidence given Human (P(E|Human))
    if high_confidence_markers >= 5:
        likelihood_human = 0.05
    elif high_confidence_markers >= 3:
        likelihood_human = 0.15
    elif high_confidence_markers >= 1:
        likelihood_human = 0.35
    else:
        likelihood_human = 0.65

    # Bayes' Theorem: P(AI|E) = P(E|AI) * P(AI) / [P(E|AI) * P(AI) + P(E|Human) * P(Human)]
    numerator = likelihood_ai * prior
    denominator = (likelihood_ai * prior) + (likelihood_human * (1 - prior))
    posterior_probability = numerator / denominator if denominator > 0 else prior

    # Adjust base score using Bayesian posterior
    bayesian_adjusted_score = base_score * (posterior_probability / prior)

    # Document length confidence adjustment
    if word_count < 300:
        confidence = 0.6
    elif word_count < 1000:
        confidence = 0.8
    else:
        confidence = 1.0

    return {
        "bayesian_adjusted_score": round(min(100, bayesian_adjusted_score), 2),
        "posterior_probability": round(posterior_probability * 100, 2),
        "prior_probability": round(prior * 100, 2),
        "likelihood_ratio": round(likelihood_ai / likelihood_human if likelihood_human > 0 else 10, 2),
        "bayesian_confidence": confidence,
    }


def detect_pattern_correlations(marker_counts: Dict[str, float]) -> Dict[str, any]:
    """
    Detect correlations between different markers.
    Certain combinations strongly indicate AI generation.
    """
    correlations = []
    correlation_score = 0

    # Strong correlation patterns
    strong_patterns = [
        # High em-dash + formal transitions + AI vocabulary
        {
            "markers": ["A1_em_dash", "D2_formal_transitions", "E1_ai_words"],
            "threshold": [3, 2, 3],
            "name": "Formal AI Writing Pattern",
            "bonus": 15,
        },
        # Uniform structure + lack of specifics + hedging
        {
            "markers": ["F1_para_uniformity", "G1_lack_specifics", "D1_hedging_overuse"],
            "threshold": [1, 1.5, 2],
            "name": "Generic Content Pattern",
            "bonus": 20,
        },
        # High transitional + enumeration + parallel structures
        {
            "markers": ["B1_transitional", "B2_enumeration", "F2_parallel_structures"],
            "threshold": [4, 1, 1],
            "name": "Structured AI Pattern",
            "bonus": 18,
        },
        # Contraction avoidance + AI words + formal transitions
        {
            "markers": ["E2_contraction_avoidance", "E1_ai_words", "D2_formal_transitions"],
            "threshold": [0.7, 4, 2],
            "name": "Overly Formal Pattern",
            "bonus": 12,
        },
    ]

    for pattern in strong_patterns:
        markers_present = []
        all_met = True

        for i, marker_key in enumerate(pattern["markers"]):
            value = marker_counts.get(marker_key, 0)
            threshold = pattern["threshold"][i]

            if value >= threshold:
                markers_present.append(f"{marker_key}={value}")
            else:
                all_met = False
                break

        if all_met:
            correlations.append({
                "pattern_name": pattern["name"],
                "markers": markers_present,
                "bonus_score": pattern["bonus"],
            })
            correlation_score += pattern["bonus"]

    # Moderate correlation patterns
    moderate_patterns = [
        # Vocabulary uniformity + sentence uniformity
        {
            "markers": ["E3_vocab_uniformity", "D4_sentence_uniformity"],
            "threshold": [1, 1],
            "name": "Overall Uniformity",
            "bonus": 10,
        },
        # Citation anomalies + generic methodology
        {
            "markers": ["I1_citation_anomalies", "I2_generic_method"],
            "threshold": [1, 2],
            "name": "Academic Red Flags",
            "bonus": 15,
        },
    ]

    for pattern in moderate_patterns:
        markers_present = []
        all_met = True

        for i, marker_key in enumerate(pattern["markers"]):
            value = marker_counts.get(marker_key, 0)
            threshold = pattern["threshold"][i]

            if value >= threshold:
                markers_present.append(f"{marker_key}={value}")
            else:
                all_met = False
                break

        if all_met:
            correlations.append({
                "pattern_name": pattern["name"],
                "markers": markers_present,
                "bonus_score": pattern["bonus"],
            })
            correlation_score += pattern["bonus"]

    return {
        "correlation_patterns": correlations,
        "correlation_bonus": min(50, correlation_score),  # Cap at 50
        "pattern_count": len(correlations),
    }


def calculate_entropy(text: str) -> float:
    """
    Calculate Shannon entropy of the text.
    Lower entropy can indicate more predictable (AI-like) text.
    """
    if not text:
        return 0.0

    # Calculate character-level entropy
    char_freq = Counter(text.lower())
    total_chars = len(text)

    entropy = 0.0
    for count in char_freq.values():
        probability = count / total_chars
        entropy -= probability * math.log2(probability)

    return round(entropy, 4)


def detect_anomalies(
    text: str,
    sentences: List[str],
    paragraphs: List[str]
) -> Dict[str, any]:
    """
    Detect statistical anomalies that might indicate AI generation.
    """
    anomalies = []
    anomaly_score = 0

    # Sentence length anomalies
    if sentences:
        sent_lengths = [len(WORD_RE.findall(s)) for s in sentences if WORD_RE.findall(s)]
        if len(sent_lengths) >= 5:
            mean_len = statistics.mean(sent_lengths)
            std_len = statistics.pstdev(sent_lengths)

            # Z-score for each sentence
            outliers = []
            for i, length in enumerate(sent_lengths):
                if std_len > 0:
                    z_score = abs((length - mean_len) / std_len)
                    if z_score > 2.5:  # Outlier
                        outliers.append(i)

            # AI text has fewer outliers (more uniform)
            outlier_ratio = len(outliers) / len(sent_lengths)
            if outlier_ratio < 0.05:  # Less than 5% outliers
                anomalies.append({
                    "type": "Uniform Sentence Lengths",
                    "description": "Unusually consistent sentence lengths",
                    "severity": "medium",
                })
                anomaly_score += 10

    # Paragraph length anomalies
    if paragraphs:
        para_lengths = [len(WORD_RE.findall(p)) for p in paragraphs if WORD_RE.findall(p)]
        if len(para_lengths) >= 3:
            # Check for suspiciously similar paragraph lengths
            max_diff = max(para_lengths) - min(para_lengths)
            avg_len = statistics.mean(para_lengths)
            if avg_len > 50 and max_diff / avg_len < 0.3:  # Less than 30% variation
                anomalies.append({
                    "type": "Uniform Paragraph Lengths",
                    "description": "Paragraphs are suspiciously similar in length",
                    "severity": "high",
                })
                anomaly_score += 15

    # Word length anomalies
    words = WORD_RE.findall(text)
    if words:
        word_lengths = [len(w) for w in words]
        if len(word_lengths) >= 50:
            # Check distribution
            short_words = sum(1 for l in word_lengths if l <= 3)
            long_words = sum(1 for l in word_lengths if l >= 8)
            short_ratio = short_words / len(word_lengths)
            long_ratio = long_words / len(word_lengths)

            # AI tends to use moderate-length words consistently
            if 0.35 < short_ratio < 0.45 and 0.08 < long_ratio < 0.15:
                anomalies.append({
                    "type": "Optimal Word Length Distribution",
                    "description": "Word lengths follow AI-typical distribution",
                    "severity": "low",
                })
                anomaly_score += 5

    return {
        "anomalies": anomalies,
        "anomaly_score": anomaly_score,
        "anomaly_count": len(anomalies),
    }


def calculate_contextual_adjustments(
    base_score: float,
    document_type: str,
    word_count: int,
    marker_counts: Dict[str, float],
    readability: Dict[str, float]
) -> Dict[str, any]:
    """
    Apply context-aware adjustments to reduce false positives.
    """
    adjustments = []
    adjustment_value = 0

    # Academic documents naturally have more formal language
    if document_type == "academic":
        formal_markers = marker_counts.get("D2_formal_transitions", 0)
        if formal_markers > 0 and formal_markers <= 4:
            adjustments.append({
                "reason": "Academic writing naturally uses formal transitions",
                "adjustment": -5,
            })
            adjustment_value -= 5

        citation_markers = marker_counts.get("I1_citation_anomalies", 0)
        if citation_markers <= 1:
            adjustments.append({
                "reason": "Citation patterns appear reasonable for academic work",
                "adjustment": -3,
            })
            adjustment_value -= 3

    # Short documents have less reliable patterns (but AI can write short text too)
    if word_count < 300:
        adjustments.append({
            "reason": "Very short document - patterns less reliable",
            "adjustment": -5,
        })
        adjustment_value -= 5
    elif word_count > 5000:
        adjustments.append({
            "reason": "Long document - patterns more reliable",
            "adjustment": +3,
        })
        adjustment_value += 3

    # Note: Removed complexity-based adjustments because modern AI models
    # excel at generating complex academic and technical text.
    # High complexity does NOT indicate human authorship.

    adjusted_score = max(0, min(100, base_score + adjustment_value))

    return {
        "contextual_adjustments": adjustments,
        "total_adjustment": adjustment_value,
        "adjusted_score": round(adjusted_score, 2),
    }
