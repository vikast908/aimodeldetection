# AWARE: AI Writing Analysis & Risk Evaluation System

## Algorithm Specification v1.0

---

## 1. System Overview

### 1.1 Purpose
Build a document analysis system that detects potential AI-generated or AI-assisted content in edited manuscripts. The system analyzes uploaded documents, identifies AI-indicative markers, applies weighted scoring, annotates findings, and returns a comprehensive risk assessment.

### 1.2 Input
- **Primary Input**: Edited document (FL file) in `.docx` format
- **Optional Input**: Original document (for comparative analysis)
- **Optional Input**: XML metadata from editing environment

### 1.3 Output
- **AI Risk Score**: 0-100 scale with probability classification
- **Annotated Document**: Original document with highlighted markers and comments
- **Detailed Report**: JSON/structured report with all findings
- **Summary**: Human-readable summary with recommendations

---

## 2. Detection Rules & Markers

### Category Overview
| Cat | Name | Description | Weight |
|-----|------|-------------|--------|
| A | High-Confidence | Strong AI indicators (em-dash, unicode, punctuation) | 30% |
| B | Moderate-Confidence | Investigation triggers (transitions, enumeration) | 15% |
| C | Contextual | Requires comparison/metadata (EoE, timing) | 15% |
| D | Stylistic | Writing style patterns (hedging, passive voice) | 5% |
| E | Vocabulary | Word choice patterns (AI-words, contractions) | 10% |
| F | Structural | Document organization (uniformity, parallelism) | 8% |
| G | Semantic | Meaning-level patterns (vagueness, circularity) | 7% |
| H | Technical | Document artifacts (fonts, clipboard, metadata) | 5% |
| I | Academic | Scholarly writing specific (citations, methods) | 3% |
| J | Behavioral | Edit behavior patterns (requires Track Changes) | 2% |

---

### 2.1 HIGH-CONFIDENCE MARKERS (Category A)
These markers provide strong evidence of AI generation. Each occurrence is significant.

#### A1: Em-Dash Usage
```
Pattern: — (U+2014) or -- converted to em-dash
Regex: /—|--/g
Weight: 15 points per occurrence
Threshold: 
  - 1-2 occurrences: Normal (may be stylistic)
  - 3-5 occurrences: Suspicious
  - 6+ occurrences: High confidence AI indicator
Scoring:
  - occurrences <= 2: score = 0
  - occurrences 3-5: score = (occurrences - 2) * 15
  - occurrences > 5: score = 45 + (occurrences - 5) * 20
Max contribution: 150 points
```

#### A2: Colon/Semicolon Density
```
Pattern: Unusual frequency of : and ; in running text (not in references/citations)
Regex: /(?<![0-9])[:;](?![0-9/])/g (exclude time formats, ratios)
Weight: 10 points per excess occurrence
Baseline: 1 per 500 words is normal
Calculation:
  - density = (count / word_count) * 500
  - excess = max(0, density - 1)
  - score = excess * 10 * (word_count / 500)
Max contribution: 100 points
```

#### A3: Unicode Subscript/Superscript Characters
```
Pattern: Unicode subscript digits (₀₁₂₃₄₅₆₇₈₉) or superscript (⁰¹²³⁴⁵⁶⁷⁸⁹)
Regex: /[₀-₉⁰-⁹ⁿ⁺⁻⁼⁽⁾]/g
Weight: 25 points per occurrence
Context: Should be formatted subscript/superscript, not Unicode characters
Scoring: score = occurrences * 25
Max contribution: 150 points
```

#### A4: Unusual Quotation Marks
```
Pattern: Straight quotes where smart quotes expected, or vice versa inconsistently
Mixed patterns: "text" vs "text" in same document
Regex: /["'].*?["']/g (analyze consistency)
Weight: 5 points per inconsistency cluster
Scoring: Measure ratio of straight to smart quotes; flag if mixed
Max contribution: 50 points
```

### 2.2 MODERATE-CONFIDENCE MARKERS (Category B)
These markers warrant investigation but are not conclusive alone.

#### B1: Transitional Word Patterns
```
Patterns (case-insensitive, sentence start):
  - "Furthermore,"
  - "Moreover,"
  - "Additionally,"
  - "Consequently,"
  - "Subsequently,"
  - "Nevertheless,"
  - "Nonetheless,"
  - "Correspondingly,"
  
Regex: /^(Furthermore|Moreover|Additionally|Consequently|Subsequently|Nevertheless|Nonetheless|Correspondingly),/gim

Weight: 8 points per occurrence after threshold
Threshold: 2 occurrences per 1000 words is normal
Calculation:
  - expected = (word_count / 1000) * 2
  - excess = max(0, count - expected)
  - score = excess * 8
Max contribution: 80 points
```

#### B2: Enumeration Patterns
```
Patterns (sentence start):
  - "Firstly," / "First,"
  - "Secondly," / "Second,"
  - "Thirdly," / "Third,"
  - "Finally,"
  - "Lastly,"
  
Regex: /^(Firstly|First|Secondly|Second|Thirdly|Third|Fourthly|Fourth|Finally|Lastly),/gim

Weight: 12 points per complete sequence (3+ items)
Detection: Track if multiple enumeration words appear in sequence across paragraphs
Scoring:
  - Single occurrence: 0 points
  - Pair (First...Second): 6 points
  - Full sequence (3+): 12 points per sequence
Max contribution: 60 points
```

#### B3: Spacing Anomalies
```
Patterns:
  - Space inside opening parenthesis: "( text"
  - Space inside closing parenthesis: "text )"
  - Space around em-dash: "word — word" (should be "word—word")
  - Space around en-dash in ranges: "10 – 20" (should be "10–20")
  - Space around forward slash: "and / or" (should be "and/or")

Regex patterns:
  - /\(\s+\S/g (space after open paren)
  - /\S\s+\)/g (space before close paren)
  - /\s—\s/g (spaces around em-dash)
  - /\d\s+–\s+\d/g (spaces around en-dash in ranges)
  - /\w\s+\/\s+\w/g (spaces around slash)

Weight: 5 points per occurrence
Max contribution: 50 points
```

#### B4: Line Break Irregularities
```
Pattern: Unexpected line breaks within paragraphs (soft returns)
Detection: Line breaks not at paragraph boundaries
Regex: /[^\n]\n(?=[a-z])/g (line break followed by lowercase = mid-sentence)
Weight: 3 points per occurrence
Max contribution: 30 points
```

#### B5: Repetitive Sentence Structures
```
Pattern: Multiple consecutive sentences with identical structure
Detection algorithm:
  1. Parse sentences
  2. Extract POS pattern (e.g., "DET NOUN VERB ADV")
  3. Flag if 3+ consecutive sentences share >70% structure similarity
  
Weight: 10 points per cluster of repetitive structures
Max contribution: 50 points
```

### 2.3 CONTEXTUAL MARKERS (Category C)
These require comparison with original document or metadata.

#### C1: Extent of Edit (EoE) Analysis
```
Requires: Original document for comparison
Calculation:
  - words_changed = count of modified words
  - total_words = document word count
  - eoe_percentage = (words_changed / total_words) * 100

Flagging:
  - EoE > 100%: Indicates more changes than original content (copy-paste likely)
  - Weight: 30 points if EoE > 100%
  - Additional: +5 points for every 10% above 100%
  
Max contribution: 80 points
```

#### C2: Large Text Chunk Detection
```
Requires: Track Changes data or XML metadata
Pattern: Large blocks of text inserted without granular edits
Detection:
  - Identify insertions > 50 words without intermediate tracked changes
  - Flag contiguous inserted text blocks
  
Weight: 20 points per large chunk detected
Max contribution: 100 points
```

#### C3: Editing Time Analysis
```
Requires: Metadata with editing duration
Baseline: ~1 hour per 1,000 words for thorough editing
Calculation:
  - expected_time = word_count / 1000 (in hours)
  - actual_time = metadata.editing_duration
  - ratio = actual_time / expected_time

Flagging:
  - ratio < 0.3: Severe flag (30 points)
  - ratio 0.3-0.5: Moderate flag (15 points)
  - ratio 0.5-0.7: Minor flag (5 points)
  - ratio >= 0.7: No flag (0 points)
  
Max contribution: 30 points
```

#### C4: Cluster Analysis
```
Requires: XML editing data
Pattern: High percentage of edits clustered in specific locations
Detection:
  - Divide document into 10 equal segments
  - Calculate edit distribution
  - Flag if >60% of edits in <20% of document
  
Weight: 15 points if clustering detected
Max contribution: 15 points
```

### 2.4 STYLISTIC MARKERS (Category D)
Subtle patterns that may indicate AI writing style.

#### D1: Hedging Language Overuse
```
Patterns:
  - "It is important to note that"
  - "It should be noted that"
  - "It is worth mentioning that"
  - "This suggests that"
  - "This indicates that"
  - "This demonstrates that"
  
Regex: /It (is|should be) (important|worth|interesting) to (note|mention|observe) that/gi

Weight: 4 points per occurrence after 2 per 1000 words
Max contribution: 40 points
```

#### D2: Overly Formal Transitions
```
Patterns:
  - "In light of the above"
  - "Taking into consideration"
  - "With regard to"
  - "In terms of"
  - "It is evident that"
  - "It can be observed that"

Weight: 3 points per occurrence
Max contribution: 30 points
```

#### D3: Passive Voice Density
```
Detection: Passive constructions per 100 words
Regex: /\b(is|are|was|were|been|being)\s+\w+ed\b/gi
Baseline: 15% passive is normal in academic writing
Flagging: Flag if >25% passive voice
Weight: 1 point per percentage point above 25%
Max contribution: 25 points
```

#### D4: Sentence Length Uniformity
```
Detection: Unusually uniform sentence lengths
Calculation:
  - Calculate standard deviation of sentence lengths
  - Natural writing: SD typically 8-15 words
  - AI writing: Often SD < 5 words (too uniform)
  
Flagging: If SD < 5, score = (5 - SD) * 10
Max contribution: 30 points
```

---

## 3. Scoring Algorithm

### 3.1 Base Score Calculation
```python
def calculate_base_score(markers):
    """
    Calculate raw score from all detected markers
    """
    category_scores = {
        'A': 0,  # High-confidence
        'B': 0,  # Moderate-confidence  
        'C': 0,  # Contextual
        'D': 0   # Stylistic
    }
    
    # Sum scores within each category (respecting max contributions)
    for marker in markers:
        category = marker.category
        points = min(marker.score, marker.max_contribution)
        category_scores[category] += points
    
    # Apply category caps
    category_caps = {'A': 450, 'B': 270, 'C': 225, 'D': 125}
    for cat in category_scores:
        category_scores[cat] = min(category_scores[cat], category_caps[cat])
    
    return category_scores
```

### 3.2 Weighted Final Score
```python
def calculate_final_score(category_scores):
    """
    Apply category weights and normalize to 0-100 scale
    """
    weights = {
        'A': 0.45,  # High-confidence markers most important
        'B': 0.25,  # Moderate markers
        'C': 0.20,  # Contextual analysis
        'D': 0.10   # Stylistic patterns
    }
    
    max_possible = {
        'A': 450 * 0.45,  # 202.5
        'B': 270 * 0.25,  # 67.5
        'C': 225 * 0.20,  # 45
        'D': 125 * 0.10   # 12.5
    }
    # Total max = 327.5
    
    weighted_score = sum(category_scores[cat] * weights[cat] for cat in weights)
    max_score = sum(max_possible.values())
    
    # Normalize to 0-100
    final_score = (weighted_score / max_score) * 100
    
    return round(final_score, 1)
```

### 3.3 Confidence Adjustment
```python
def adjust_for_confidence(final_score, document_length, markers_found):
    """
    Adjust score based on statistical confidence
    """
    # Short documents have less reliable scores
    if document_length < 500:
        confidence_factor = 0.7
    elif document_length < 1000:
        confidence_factor = 0.85
    else:
        confidence_factor = 1.0
    
    # Few markers = lower confidence in high scores
    if markers_found < 3 and final_score > 50:
        final_score = final_score * 0.8
    
    return {
        'score': round(final_score, 1),
        'confidence': confidence_factor,
        'adjusted_score': round(final_score * confidence_factor, 1)
    }
```

### 3.4 Comparative Scoring (When Original Available)
```python
def calculate_comparative_score(original_markers, edited_markers):
    """
    Score based on INCREASE in markers from original to edited
    """
    introduced_markers = []
    
    for marker_type in edited_markers:
        original_count = original_markers.get(marker_type, 0)
        edited_count = edited_markers[marker_type]
        
        # Only score markers INTRODUCED by editing
        introduced = max(0, edited_count - original_count)
        if introduced > 0:
            introduced_markers.append({
                'type': marker_type,
                'original': original_count,
                'edited': edited_count,
                'introduced': introduced
            })
    
    # Recalculate score based only on introduced markers
    return calculate_base_score(introduced_markers)
```

---

## 4. Risk Classification

### 4.1 Score Thresholds
```
Score Range    | Classification      | Action Required
---------------|---------------------|------------------
0-15           | MINIMAL RISK        | No action needed
16-35          | LOW RISK            | Monitor only
36-55          | MODERATE RISK       | Review recommended
56-75          | HIGH RISK           | Investigation required
76-100         | CRITICAL RISK       | Immediate escalation
```

### 4.2 Classification Logic
```python
def classify_risk(score, high_confidence_markers):
    """
    Classify risk level with override conditions
    """
    # Base classification
    if score <= 15:
        classification = 'MINIMAL'
    elif score <= 35:
        classification = 'LOW'
    elif score <= 55:
        classification = 'MODERATE'
    elif score <= 75:
        classification = 'HIGH'
    else:
        classification = 'CRITICAL'
    
    # Override: Multiple high-confidence markers elevate risk
    if high_confidence_markers >= 3 and classification in ['MINIMAL', 'LOW']:
        classification = 'MODERATE'
    
    if high_confidence_markers >= 5 and classification == 'MODERATE':
        classification = 'HIGH'
    
    return classification
```

### 4.3 Probability Mapping (For Client Communication)
```
Classification  | Probability Label           | Response Protocol
----------------|-----------------------------|-----------------
MINIMAL/LOW     | Low Probability of AI Use   | Explain & provide evidence
MODERATE        | Medium Probability of AI Use| Offer re-edit; investigate
HIGH/CRITICAL   | High Probability of AI Use  | Significant remediation
```

---

## 5. Annotation Specification

### 5.1 Annotation Types
```python
annotation_types = {
    'HIGHLIGHT': {
        'HIGH_CONFIDENCE': '#FF6B6B',    # Red
        'MODERATE_CONFIDENCE': '#FFB347', # Orange
        'CONTEXTUAL': '#87CEEB',          # Light blue
        'STYLISTIC': '#DDA0DD'            # Plum
    },
    'COMMENT': {
        'format': '[AWARE-{category}{id}] {marker_type}: {description}',
        'example': '[AWARE-A1] Em-dash: AI-indicative punctuation detected'
    }
}
```

### 5.2 Annotation Content Structure
```python
def create_annotation(marker):
    """
    Generate annotation for a detected marker
    """
    return {
        'id': f"AWARE-{marker.category}{marker.id}",
        'type': marker.name,
        'category': marker.category,
        'severity': get_severity(marker.category),
        'location': {
            'paragraph': marker.paragraph_index,
            'start_char': marker.start,
            'end_char': marker.end,
            'text_snippet': marker.matched_text
        },
        'highlight_color': annotation_types['HIGHLIGHT'][marker.severity],
        'comment': {
            'title': f"{marker.name} Detected",
            'body': marker.description,
            'recommendation': marker.recommendation
        },
        'score_contribution': marker.score
    }
```

### 5.3 Marker Descriptions for Annotations
```yaml
A1_em_dash:
  title: "Em-Dash Usage"
  description: "Em-dash (—) detected. Excessive em-dash usage is a strong indicator of AI-generated text."
  recommendation: "Review for necessity. Consider replacing with commas, colons, or parentheses."

A2_colon_semicolon:
  title: "Unusual Punctuation Density"
  description: "High frequency of colons/semicolons detected in running text."
  recommendation: "Verify punctuation is contextually appropriate and not artifacts of AI generation."

A3_unicode_subscript:
  title: "Unicode Subscript/Superscript"
  description: "Unicode subscript/superscript characters found instead of proper formatting."
  recommendation: "Replace with properly formatted subscript/superscript."

B1_transitional:
  title: "AI-Style Transition"
  description: "Transitional phrase pattern commonly associated with AI writing."
  recommendation: "Consider varying sentence openings for more natural flow."

B2_enumeration:
  title: "Enumeration Pattern"
  description: "Firstly/Secondly/Finally pattern detected - common in AI-generated text."
  recommendation: "Review if enumeration is necessary or can be restructured."

B3_spacing:
  title: "Spacing Anomaly"
  description: "Unusual spacing around punctuation detected."
  recommendation: "Correct spacing per style guidelines."

D1_hedging:
  title: "Hedging Language"
  description: "Overuse of hedging phrases typical of AI-generated academic text."
  recommendation: "Consider more direct phrasing where appropriate."
```

---

## 6. Output Specification

### 6.1 JSON Report Structure
```json
{
  "analysis_id": "uuid",
  "timestamp": "ISO-8601",
  "document": {
    "filename": "string",
    "word_count": "integer",
    "paragraph_count": "integer",
    "has_original": "boolean"
  },
  "scores": {
    "raw_score": "float",
    "adjusted_score": "float",
    "confidence": "float",
    "category_breakdown": {
      "A_high_confidence": "float",
      "B_moderate_confidence": "float", 
      "C_contextual": "float",
      "D_stylistic": "float"
    }
  },
  "classification": {
    "risk_level": "MINIMAL|LOW|MODERATE|HIGH|CRITICAL",
    "probability_label": "string",
    "response_protocol": "string"
  },
  "markers": [
    {
      "id": "string",
      "category": "A|B|C|D",
      "type": "string",
      "count": "integer",
      "locations": ["array of location objects"],
      "score_contribution": "float",
      "description": "string"
    }
  ],
  "summary": {
    "total_markers_found": "integer",
    "high_confidence_markers": "integer",
    "primary_concerns": ["array of strings"],
    "recommendation": "string"
  },
  "comparative_analysis": {
    "available": "boolean",
    "original_marker_count": "integer",
    "introduced_marker_count": "integer",
    "eoe_percentage": "float"
  }
}
```

### 6.2 Summary Text Generation
```python
def generate_summary(analysis_result):
    """
    Generate human-readable summary
    """
    templates = {
        'MINIMAL': "Analysis indicates minimal risk of AI involvement. {marker_count} minor markers detected, consistent with normal human editing patterns.",
        
        'LOW': "Analysis indicates low risk of AI involvement. {marker_count} markers detected. Some patterns noted but within acceptable thresholds for human editing.",
        
        'MODERATE': "Analysis indicates moderate risk of potential AI involvement. {marker_count} markers detected including {high_conf} high-confidence indicators. Manual review recommended. Primary concerns: {concerns}.",
        
        'HIGH': "Analysis indicates high risk of AI involvement. {marker_count} markers detected with {high_conf} high-confidence indicators. Investigation required. Primary concerns: {concerns}.",
        
        'CRITICAL': "Analysis indicates critical risk of extensive AI involvement. {marker_count} markers detected with {high_conf} high-confidence indicators strongly suggesting AI-generated or AI-rewritten content. Immediate escalation required. Primary concerns: {concerns}."
    }
    
    return templates[analysis_result.classification].format(
        marker_count=analysis_result.total_markers,
        high_conf=analysis_result.high_confidence_count,
        concerns=', '.join(analysis_result.primary_concerns[:3])
    )
```

---

## 7. Implementation Guidelines

### 7.1 Document Processing Pipeline
```
1. EXTRACT
   ├── Parse .docx file
   ├── Extract plain text
   ├── Extract formatting metadata
   ├── Extract Track Changes (if present)
   └── Extract XML data (if available)

2. ANALYZE
   ├── Run Category A markers (high-confidence)
   ├── Run Category B markers (moderate)
   ├── Run Category C markers (contextual) [if data available]
   ├── Run Category D markers (stylistic)
   └── Collect all marker instances with locations

3. SCORE
   ├── Calculate category scores
   ├── Apply weights
   ├── Normalize to 0-100
   ├── Adjust for confidence
   └── Classify risk level

4. ANNOTATE
   ├── Generate annotations for each marker
   ├── Apply highlights to document
   ├── Insert comments
   └── Create annotated copy

5. REPORT
   ├── Generate JSON report
   ├── Generate summary text
   ├── Package annotated document
   └── Return results
```

### 7.2 Required Libraries
```
- python-docx: Document parsing and annotation
- re: Regular expression matching
- spacy: NLP for sentence parsing and POS tagging
- numpy: Statistical calculations
- json: Report generation
```

### 7.3 Performance Considerations
```
- Cache compiled regex patterns
- Process document in streaming fashion for large files
- Parallelize independent marker detection
- Limit annotation density (max 50 annotations per page)
```

### 7.4 Error Handling
```python
error_responses = {
    'INVALID_FORMAT': "Document format not supported. Please upload .docx file.",
    'EMPTY_DOCUMENT': "Document appears to be empty or unreadable.",
    'PROCESSING_ERROR': "Error processing document. Please try again.",
    'TIMEOUT': "Analysis timed out. Document may be too large."
}
```

---

## 8. Testing & Calibration

### 8.1 Calibration Dataset Requirements
```
- 50+ documents with known AI content (positive samples)
- 50+ documents with confirmed human-only editing (negative samples)
- Mix of subject areas and document lengths
- Include edge cases (AI-edited human text, human-edited AI text)
```

### 8.2 Threshold Tuning
```
Initial thresholds should be tuned to achieve:
- False Positive Rate < 10% (don't flag good human editing)
- False Negative Rate < 5% (don't miss AI content)
- Precision > 85% for HIGH/CRITICAL classifications
```

### 8.3 Validation Metrics
```python
metrics = {
    'accuracy': 'Overall correct classifications',
    'precision': 'True positives / All positives',
    'recall': 'True positives / Actual positives', 
    'f1_score': 'Harmonic mean of precision and recall',
    'auc_roc': 'Area under ROC curve'
}
```

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2025 | Initial specification |

---

## 10. Additional Detection Rules (Extended)

### 10.1 VOCABULARY MARKERS (Category E)
AI models have characteristic word preferences that appear with unusual frequency.

#### E1: AI-Favorite Words
```
High-frequency AI words (flag if 3+ different words appear):
  - "delve" / "delving"
  - "crucial" / "crucially"
  - "pivotal"
  - "multifaceted"
  - "nuanced"
  - "comprehensive"
  - "robust"
  - "leverage" (as verb)
  - "facilitate"
  - "utilize" (instead of "use")
  - "landscape" (metaphorical)
  - "paradigm"
  - "synergy"
  - "holistic"
  - "streamline"
  - "foster"
  - "underscores"
  - "realm"
  - "encompasses"
  - "intricate"
  - "notably"
  - "essentially"
  - "arguably"

Regex: /\b(delve|delving|crucial|crucially|pivotal|multifaceted|nuanced|comprehensive|robust|leverage[sd]?|facilitate[sd]?|utilize[sd]?|landscape|paradigm|synergy|holistic|streamline[sd]?|foster[sd]?|underscores?|realm|encompasses?|intricate|notably|essentially|arguably)\b/gi

Scoring:
  - 1-2 words: 0 points (normal vocabulary)
  - 3-5 different words: 15 points
  - 6-8 different words: 30 points
  - 9+ different words: 50 points
  - Frequency multiplier: If any word appears 3+ times, add 10 points

Max contribution: 70 points
```

#### E2: Contraction Avoidance
```
Pattern: AI tends to avoid contractions, writing formally
Detection:
  - Count potential contraction opportunities (do not, cannot, will not, etc.)
  - Count actual contractions used
  - Calculate avoidance ratio

Expandable forms to check:
  - "do not" vs "don't"
  - "does not" vs "doesn't"
  - "did not" vs "didn't"
  - "cannot" vs "can't"
  - "will not" vs "won't"
  - "would not" vs "wouldn't"
  - "should not" vs "shouldn't"
  - "could not" vs "couldn't"
  - "is not" vs "isn't"
  - "are not" vs "aren't"
  - "have not" vs "haven't"
  - "has not" vs "hasn't"
  - "it is" vs "it's"
  - "that is" vs "that's"

Calculation:
  - expanded_forms = count of "do not", "cannot", etc.
  - contractions = count of "don't", "can't", etc.
  - total = expanded_forms + contractions
  - avoidance_ratio = expanded_forms / total (if total > 5)
  
Scoring:
  - avoidance_ratio > 0.9 AND total > 10: 25 points
  - avoidance_ratio > 0.8 AND total > 10: 15 points
  - avoidance_ratio > 0.7 AND total > 10: 5 points

Max contribution: 25 points
```

#### E3: Vocabulary Sophistication Uniformity
```
Pattern: Human writing varies in sophistication; AI maintains consistent level
Detection:
  - Calculate average word length per paragraph
  - Calculate standard deviation across paragraphs
  - Flag if SD is unusually low (too uniform)

Natural writing: SD of avg word length typically 0.5-1.5
AI writing: SD often < 0.3

Scoring:
  - SD < 0.2: 20 points
  - SD 0.2-0.3: 10 points
  - SD > 0.3: 0 points

Max contribution: 20 points
```

#### E4: Filler Phrase Patterns
```
AI-characteristic filler phrases:
  - "In today's [world/society/age]"
  - "In the realm of"
  - "It's worth noting that"
  - "At its core"
  - "When it comes to"
  - "In essence"
  - "By and large"
  - "All in all"
  - "At the end of the day"
  - "The fact that"
  - "In order to" (instead of "to")
  - "Due to the fact that" (instead of "because")
  - "In the context of"
  - "With respect to"
  - "In a nutshell"

Weight: 5 points per phrase occurrence
Max contribution: 40 points
```

### 10.2 STRUCTURAL MARKERS (Category F)
Patterns in document organization and content structure.

#### F1: Paragraph Length Uniformity
```
Pattern: AI generates paragraphs of similar length
Detection:
  - Calculate word count per paragraph
  - Calculate coefficient of variation (CV = SD/mean)
  
Natural writing: CV typically 0.4-0.8
AI writing: CV often < 0.25

Scoring:
  - CV < 0.15: 25 points
  - CV 0.15-0.25: 15 points
  - CV 0.25-0.35: 5 points
  - CV > 0.35: 0 points

Max contribution: 25 points
```

#### F2: Perfect Parallel Structures
```
Pattern: AI creates overly symmetrical lists and comparisons
Detection:
  - Identify list items or comparative statements
  - Check if they follow identical grammatical patterns
  - Flag if 4+ items have exact same structure

Example (AI-like):
  - "The system improves efficiency."
  - "The system reduces costs."
  - "The system enhances quality."
  - "The system increases productivity."

Weight: 10 points per perfect parallel set (4+ items)
Max contribution: 30 points
```

#### F3: Balanced Argument Pattern
```
Pattern: AI often presents artificially balanced pros/cons
Detection:
  - Identify advantage/disadvantage or pro/con sections
  - Check if counts are suspiciously equal
  - Flag if exactly matched (e.g., 5 pros, 5 cons)

Weight: 15 points if perfectly balanced with 4+ items each side
Max contribution: 15 points
```

#### F4: Formulaic Conclusions
```
Pattern: AI conclusions follow predictable templates
Markers:
  - "In conclusion" at start of final paragraph
  - Summary that lists all previously mentioned points
  - Ends with generic forward-looking statement
  - Contains phrases like "it is clear that", "we can see that"

Detection: Check final paragraph for template matches
Weight: 10 points if 2+ formulaic elements present
Max contribution: 20 points
```

#### F5: Introduction-Body-Conclusion Rigidity
```
Pattern: AI strictly follows essay structure even when inappropriate
Detection:
  - Identify if document has clear intro/body/conclusion
  - Check if intro previews all points in order
  - Check if conclusion restates all points in order
  - Flag if structure is mechanically perfect

Weight: 10 points if rigidly structured with point-by-point correspondence
Max contribution: 10 points
```

### 10.3 SEMANTIC MARKERS (Category G)
Meaning-level patterns indicating AI generation.

#### G1: Lack of Specific Examples
```
Pattern: AI makes claims without concrete examples or data
Detection:
  - Count specific numbers, dates, names, places
  - Count vague quantifiers ("many", "some", "various", "numerous")
  - Calculate specificity ratio

Vague quantifiers:
  - "many studies show"
  - "research indicates"
  - "experts agree"
  - "some researchers"
  - "various factors"
  - "numerous examples"
  - "several aspects"

Calculation:
  - specific_items = count of numbers, proper nouns, specific references
  - vague_items = count of vague quantifiers
  - ratio = vague_items / (specific_items + 1)

Scoring:
  - ratio > 3.0: 25 points
  - ratio 2.0-3.0: 15 points
  - ratio 1.0-2.0: 5 points

Max contribution: 25 points
```

#### G2: Circular Definitions
```
Pattern: AI sometimes defines terms using the term itself
Detection: 
  - Extract sentences containing "is defined as", "refers to", "means"
  - Check if the subject word appears in the definition
  
Example: "Quality management is the management of quality..."

Weight: 15 points per circular definition
Max contribution: 30 points
```

#### G3: Generic Statements Without Substance
```
Pattern: AI fills space with truisms and obvious statements
Markers:
  - "X is important"
  - "X plays a crucial role"
  - "X has both advantages and disadvantages"
  - "X is a complex topic"
  - "X requires careful consideration"
  - "X is essential for success"
  - "X has become increasingly important"

Weight: 3 points per generic statement
Max contribution: 30 points
```

#### G4: Hedging Clusters
```
Pattern: Multiple hedging words in single sentence (AI over-hedges)
Hedging words:
  - "may", "might", "could", "possibly", "potentially"
  - "perhaps", "arguably", "seemingly", "apparently"
  - "tend to", "appear to", "seem to"
  - "somewhat", "relatively", "fairly", "rather"

Detection: Flag sentences with 3+ hedging words
Weight: 8 points per over-hedged sentence
Max contribution: 40 points
```

### 10.4 TECHNICAL ARTIFACTS (Category H)
Document metadata and formatting signals.

#### H1: Font Inconsistencies
```
Pattern: Copy-pasted AI text may have different font properties
Detection:
  - Extract font information from document XML
  - Identify sections with different fonts/sizes
  - Flag abrupt font changes not at section boundaries

Weight: 10 points per unexplained font change cluster
Max contribution: 40 points
```

#### H2: Style Inconsistencies
```
Pattern: Mixed formatting styles indicating external paste
Detection:
  - Check for mixed heading styles
  - Check for inconsistent list formatting
  - Check for varying paragraph spacing

Weight: 5 points per inconsistency type found
Max contribution: 25 points
```

#### H3: Metadata Timestamp Anomalies
```
Pattern: Document metadata shows suspicious timing
Detection:
  - Compare creation time vs modification time
  - Check revision count vs content amount
  - Flag if large document has minimal revisions

Scoring:
  - Document >5000 words with <3 revisions: 20 points
  - Modification time < creation time + 10 min for large doc: 15 points

Max contribution: 25 points
```

#### H4: Hidden Text or Comments
```
Pattern: Remnant AI instructions or prompts
Detection:
  - Search for hidden text
  - Search for comments containing AI tool names
  - Search for prompt-like content

Keywords to flag:
  - "ChatGPT", "Claude", "GPT-4", "Gemini", "AI assistant"
  - "Write me", "Generate", "Create a", "Help me write"
  - "As an AI", "As a language model"

Weight: 50 points if AI-related remnants found (high confidence)
Max contribution: 50 points
```

#### H5: Clipboard Artifacts
```
Pattern: Special characters from web/AI tool copy-paste
Detection:
  - Zero-width spaces (U+200B)
  - Zero-width joiners (U+200D)
  - Non-breaking spaces in unusual places
  - Object replacement characters (U+FFFC)
  - Unusual whitespace characters

Regex: /[\u200B\u200C\u200D\uFEFF\u00A0\uFFFC]/g

Weight: 10 points per cluster of artifacts
Max contribution: 40 points
```

### 10.5 ACADEMIC-SPECIFIC MARKERS (Category I)
Patterns specific to academic/scientific writing.

#### I1: Citation Anomalies
```
Pattern: AI often creates plausible but incorrect citations
Detection:
  - Check citation format consistency
  - Flag citations with suspiciously round years (2020, 2021, 2022)
  - Flag "et al." overuse without corresponding full citations
  - Flag citations that don't match reference list

Weight: 15 points per citation anomaly cluster
Max contribution: 45 points
Note: Requires reference list parsing for full detection
```

#### I2: Generic Methodology Descriptions
```
Pattern: AI writes vague methodology without specific details
Markers:
  - "standard procedures were followed"
  - "appropriate statistical methods"
  - "conventional techniques"
  - "established protocols"
  - Lack of specific equipment/software names
  - Lack of specific parameter values

Weight: 10 points if multiple vague methodology phrases detected
Max contribution: 20 points
```

#### I3: Results Without Data
```
Pattern: AI describes results without actual numbers
Detection:
  - Identify results/findings sections
  - Check for presence of specific numerical data
  - Flag if results described qualitatively only

Markers:
  - "showed significant improvement"
  - "demonstrated positive results"
  - "indicated a trend"
  - Without corresponding p-values, percentages, measurements

Weight: 15 points if results section lacks quantitative data
Max contribution: 15 points
```

#### I4: Misused Technical Terms
```
Pattern: AI sometimes uses technical terms slightly incorrectly
Detection:
  - Build domain-specific terminology checker
  - Flag terms used in wrong context
  - Flag made-up compound terms

Weight: 20 points per clear terminology misuse
Max contribution: 40 points
Note: Requires domain-specific dictionaries
```

### 10.6 BEHAVIORAL MARKERS (Category J)
Patterns based on editing behavior (requires Track Changes/metadata).

#### J1: Wholesale Replacement Pattern
```
Pattern: Human edits are scattered; AI replacement is wholesale
Detection:
  - Analyze Track Changes distribution
  - Calculate ratio of modified paragraphs to total paragraphs
  - Flag if >80% of paragraphs have changes AND changes are complete rewrites

Scoring:
  - >80% paragraphs with >50% rewrite each: 35 points
  - >60% paragraphs with >50% rewrite each: 20 points
  - >40% paragraphs with >50% rewrite each: 10 points

Max contribution: 35 points
```

#### J2: Edit Granularity Analysis
```
Pattern: Human edits are word/phrase level; AI replacement is sentence/paragraph level
Detection:
  - Categorize each edit by size (word/phrase/sentence/paragraph)
  - Calculate distribution
  - Flag if >50% of edits are sentence-level or larger

Natural editing: ~70% word/phrase level, ~30% sentence+ level
AI replacement: Often >60% sentence+ level

Scoring:
  - >70% sentence+ level edits: 25 points
  - >50% sentence+ level edits: 15 points

Max contribution: 25 points
```

#### J3: Revision Consistency
```
Pattern: Human revisions show learning/adaptation; AI is consistent from start
Detection:
  - Divide edits chronologically into thirds
  - Compare edit patterns across thirds
  - Human editors typically have more corrections in later thirds (fatigue)
  - AI-replaced content shows uniform "edit" distribution

Weight: 15 points if edit distribution is suspiciously uniform
Max contribution: 15 points
```

#### J4: Time-Gap Analysis
```
Pattern: Large text additions without corresponding time gaps
Detection (requires timestamp metadata):
  - Identify insertions >100 words
  - Check editing time around insertion
  - Flag if large insertion has <2 minutes attributed time

Baseline: ~30 words/minute for typing from thought
AI paste: Can be 500+ words in seconds

Scoring:
  - >200 words added with <1 min gap: 30 points
  - >100 words added with <30 sec gap: 25 points

Max contribution: 30 points
```

---

## 11. Updated Scoring with New Categories

### 11.1 Extended Category Weights
```python
weights = {
    'A': 0.30,  # High-confidence markers (reduced to accommodate new categories)
    'B': 0.15,  # Moderate markers
    'C': 0.15,  # Contextual analysis
    'D': 0.05,  # Stylistic patterns
    'E': 0.10,  # Vocabulary markers (NEW)
    'F': 0.08,  # Structural markers (NEW)
    'G': 0.07,  # Semantic markers (NEW)
    'H': 0.05,  # Technical artifacts (NEW)
    'I': 0.03,  # Academic-specific (NEW) - only if applicable
    'J': 0.02   # Behavioral markers (NEW) - only if data available
}

category_caps = {
    'A': 450,
    'B': 270,
    'C': 225,
    'D': 125,
    'E': 155,  # NEW
    'F': 100,  # NEW
    'G': 125,  # NEW
    'H': 180,  # NEW
    'I': 120,  # NEW
    'J': 105   # NEW
}
```

### 11.2 Adaptive Weighting
```python
def get_adaptive_weights(document_type, available_data):
    """
    Adjust weights based on document type and available metadata
    """
    base_weights = {...}  # as above
    
    # If academic document, increase Category I weight
    if document_type == 'academic':
        base_weights['I'] = 0.08
        base_weights['A'] = 0.27  # Reduce A to compensate
    
    # If no Track Changes available, redistribute J weight
    if not available_data.get('track_changes'):
        base_weights['J'] = 0
        base_weights['A'] += 0.02
    
    # If no timing metadata, reduce C weight
    if not available_data.get('timing_metadata'):
        base_weights['C'] = 0.10
        base_weights['E'] += 0.05
    
    # Normalize weights to sum to 1.0
    total = sum(base_weights.values())
    return {k: v/total for k, v in base_weights.items()}
```

---

## 12. Enhanced Output Report

### 12.1 Extended JSON Structure
```json
{
  "analysis_id": "uuid",
  "timestamp": "ISO-8601",
  "version": "2.0",
  "document": {
    "filename": "string",
    "word_count": "integer",
    "paragraph_count": "integer",
    "sentence_count": "integer",
    "document_type": "academic|business|general",
    "has_original": "boolean",
    "has_track_changes": "boolean",
    "has_timing_data": "boolean"
  },
  "scores": {
    "raw_score": "float",
    "adjusted_score": "float",
    "confidence": "float",
    "category_breakdown": {
      "A_high_confidence": {"score": "float", "markers_found": "int"},
      "B_moderate_confidence": {"score": "float", "markers_found": "int"},
      "C_contextual": {"score": "float", "markers_found": "int"},
      "D_stylistic": {"score": "float", "markers_found": "int"},
      "E_vocabulary": {"score": "float", "markers_found": "int"},
      "F_structural": {"score": "float", "markers_found": "int"},
      "G_semantic": {"score": "float", "markers_found": "int"},
      "H_technical": {"score": "float", "markers_found": "int"},
      "I_academic": {"score": "float", "markers_found": "int", "applicable": "boolean"},
      "J_behavioral": {"score": "float", "markers_found": "int", "data_available": "boolean"}
    }
  },
  "classification": {
    "risk_level": "MINIMAL|LOW|MODERATE|HIGH|CRITICAL",
    "probability_label": "string",
    "confidence_interval": {"low": "float", "high": "float"},
    "response_protocol": "string"
  },
  "marker_details": {
    "total_markers": "integer",
    "by_category": {
      "A": [{"type": "string", "count": "int", "examples": ["string"]}],
      "B": [...],
      ...
    }
  },
  "red_flags": [
    {
      "severity": "HIGH|MEDIUM",
      "description": "string",
      "evidence": "string",
      "recommendation": "string"
    }
  ],
  "linguistic_profile": {
    "avg_sentence_length": "float",
    "sentence_length_variance": "float",
    "vocabulary_diversity": "float",
    "passive_voice_percentage": "float",
    "contraction_usage_ratio": "float",
    "hedging_density": "float"
  },
  "summary": {
    "headline": "string",
    "key_findings": ["string"],
    "recommendation": "string",
    "confidence_statement": "string"
  }
}
```

### 12.2 Visual Report Elements
```
Generate visual elements for report:

1. RISK GAUGE
   - Semicircular gauge showing 0-100 score
   - Color gradient: Green → Yellow → Orange → Red
   - Needle pointing to score
   
2. CATEGORY BREAKDOWN CHART
   - Radar/spider chart showing all 10 categories
   - Normalized scores per category
   - Highlight categories exceeding thresholds

3. MARKER HEATMAP
   - Document visualization
   - Color intensity by marker density per section
   - Clickable to show specific markers

4. CONFIDENCE INDICATOR
   - Visual representation of analysis confidence
   - Based on document length and data availability
```

---

## 13. Calibration & Thresholds Configuration

### 13.1 Configurable Thresholds File
```yaml
# thresholds.yaml - Adjust based on calibration results

markers:
  A1_em_dash:
    normal_threshold: 2
    suspicious_threshold: 5
    base_weight: 15
    excess_weight: 20
    max_contribution: 150
    
  A2_colon_semicolon:
    baseline_per_500_words: 1.0
    weight_per_excess: 10
    max_contribution: 100
    
  E1_ai_words:
    min_unique_words_to_flag: 3
    frequency_multiplier_threshold: 3
    scores:
      low: 15      # 3-5 words
      medium: 30   # 6-8 words
      high: 50     # 9+ words
    max_contribution: 70

  # ... continue for all markers

risk_classification:
  minimal_max: 15
  low_max: 35
  moderate_max: 55
  high_max: 75
  # Above 75 = critical

confidence_adjustment:
  short_document_threshold: 500
  medium_document_threshold: 1000
  short_document_factor: 0.7
  medium_document_factor: 0.85
  min_markers_for_high_confidence: 3

category_weights:
  A: 0.30
  B: 0.15
  C: 0.15
  D: 0.05
  E: 0.10
  F: 0.08
  G: 0.07
  H: 0.05
  I: 0.03
  J: 0.02
```

### 13.2 A/B Testing Framework
```python
def run_ab_test(documents, config_a, config_b):
    """
    Compare two threshold configurations
    """
    results_a = [analyze(doc, config_a) for doc in documents]
    results_b = [analyze(doc, config_b) for doc in documents]
    
    metrics = {
        'config_a': calculate_metrics(results_a, ground_truth),
        'config_b': calculate_metrics(results_b, ground_truth)
    }
    
    return metrics
```

---

## 14. Edge Cases & Special Handling

### 14.1 Document Type Detection
```python
def detect_document_type(text, metadata):
    """
    Automatically detect document type for appropriate scoring
    """
    academic_signals = [
        'abstract', 'introduction', 'methodology', 'results',
        'discussion', 'conclusion', 'references', 'et al.',
        'p-value', 'hypothesis', 'statistical'
    ]
    
    business_signals = [
        'executive summary', 'stakeholder', 'ROI', 'KPI',
        'deliverable', 'milestone', 'quarterly'
    ]
    
    academic_score = sum(1 for s in academic_signals if s.lower() in text.lower())
    business_score = sum(1 for s in business_signals if s.lower() in text.lower())
    
    if academic_score > 5:
        return 'academic'
    elif business_score > 3:
        return 'business'
    else:
        return 'general'
```

### 14.2 Non-English Content Handling
```python
def handle_non_english(text):
    """
    Detect and handle non-English content
    """
    # Some markers don't apply to non-English
    # Adjust scoring accordingly
    
    english_ratio = detect_english_percentage(text)
    
    if english_ratio < 0.3:
        return {
            'status': 'non_english',
            'message': 'Document is primarily non-English. Limited analysis available.',
            'applicable_categories': ['H']  # Only technical artifacts
        }
    elif english_ratio < 0.7:
        return {
            'status': 'mixed_language',
            'message': 'Document contains mixed languages. Some markers may not apply.',
            'confidence_adjustment': 0.7
        }
    else:
        return {'status': 'english', 'confidence_adjustment': 1.0}
```

### 14.3 Known False Positive Patterns
```yaml
# Patterns that commonly trigger false positives

false_positive_mitigations:
  
  em_dash_exceptions:
    - Legal documents (em-dashes common in citations)
    - British English style (em-dashes more common)
    - Dialogue-heavy content
    
  transitional_word_exceptions:
    - Academic papers (genuinely need transitions)
    - Documents under 500 words (limited sample)
    - Technical documentation
    
  enumeration_exceptions:
    - Instructional content
    - Process documentation
    - List-based formats

mitigation_rules:
  - If document_type == 'legal': reduce A1_weight by 50%
  - If document_type == 'academic' AND word_count > 5000: increase B1_threshold by 1.5x
  - If detected_style == 'instructional': exclude F2 entirely
```

---

## 15. API Specification

### 15.1 Endpoints
```
POST /api/v1/analyze
  - Upload document for analysis
  - Returns: analysis_id, estimated_time

GET /api/v1/analysis/{analysis_id}
  - Get analysis results
  - Returns: full JSON report

GET /api/v1/analysis/{analysis_id}/annotated
  - Download annotated document
  - Returns: .docx file with highlights and comments

POST /api/v1/analyze/compare
  - Upload original + edited for comparative analysis
  - Returns: analysis focusing on introduced markers

GET /api/v1/config/thresholds
  - Get current threshold configuration

PUT /api/v1/config/thresholds
  - Update threshold configuration (admin only)
```

### 15.2 Request/Response Examples
```json
// POST /api/v1/analyze
// Request:
{
  "document": "base64_encoded_docx",
  "options": {
    "document_type": "auto|academic|business|general",
    "include_annotations": true,
    "detail_level": "summary|standard|detailed"
  }
}

// Response:
{
  "analysis_id": "abc123",
  "status": "processing",
  "estimated_completion": "2025-01-22T10:30:00Z",
  "callback_url": "/api/v1/analysis/abc123"
}
```

---

## 16. Appendix: Quick Reference

### Marker Categories at a Glance
| Category | Weight | Focus | Max Points |
|----------|--------|-------|------------|
| A | 30% | High-confidence markers (em-dash, unicode, punctuation density) | 450 |
| B | 15% | Moderate markers (transitions, enumeration, spacing) | 270 |
| C | 15% | Contextual (EoE, chunks, timing, clusters) | 225 |
| D | 5% | Stylistic (hedging, passive voice, uniformity) | 125 |
| E | 10% | Vocabulary (AI-words, contractions, filler phrases) | 155 |
| F | 8% | Structural (paragraph uniformity, parallel structures) | 100 |
| G | 7% | Semantic (specificity, circular definitions, generics) | 125 |
| H | 5% | Technical (fonts, clipboard artifacts, metadata) | 180 |
| I | 3% | Academic-specific (citations, methodology, results) | 120 |
| J | 2% | Behavioral (edit patterns, granularity, timing) | 105 |

### Risk Levels Quick Reference
| Score | Level | Color | Action |
|-------|-------|-------|--------|
| 0-15 | MINIMAL | 🟢 Green | None |
| 16-35 | LOW | 🟡 Yellow | Monitor |
| 36-55 | MODERATE | 🟠 Orange | Review |
| 56-75 | HIGH | 🔴 Red | Investigate |
| 76-100 | CRITICAL | ⚫ Black | Escalate |

---

## 17. Composite Pattern Detection

### 17.1 High-Confidence Combinations
Certain marker combinations together provide very strong evidence of AI use.

```python
composite_patterns = {
    'SMOKING_GUN_1': {
        'name': 'Copy-Paste Signature',
        'required_markers': ['A1_em_dash >= 5', 'H5_clipboard_artifacts', 'J4_time_gap'],
        'bonus_score': 50,
        'auto_classify': 'HIGH',
        'description': 'Multiple em-dashes + clipboard artifacts + suspicious timing'
    },
    
    'SMOKING_GUN_2': {
        'name': 'AI Writing Style Bundle',
        'required_markers': ['E1_ai_words >= 5', 'B1_transitional >= 4', 'F1_para_uniformity'],
        'bonus_score': 40,
        'auto_classify': 'HIGH',
        'description': 'AI vocabulary + transitional patterns + uniform structure'
    },
    
    'SMOKING_GUN_3': {
        'name': 'Wholesale Replacement Evidence',
        'required_markers': ['C1_eoe > 100%', 'C2_large_chunks >= 2', 'J1_wholesale'],
        'bonus_score': 60,
        'auto_classify': 'CRITICAL',
        'description': 'High EoE + large chunk insertions + wholesale edit pattern'
    },
    
    'SUSPICIOUS_COMBO_1': {
        'name': 'Academic AI Pattern',
        'required_markers': ['G1_lack_specifics', 'I2_generic_method', 'D1_hedging_overuse'],
        'bonus_score': 25,
        'auto_classify': 'MODERATE',
        'description': 'Vague content + generic methodology + excessive hedging'
    },
    
    'SUSPICIOUS_COMBO_2': {
        'name': 'Format Inconsistency Bundle',
        'required_markers': ['H1_font_inconsistent', 'H2_style_inconsistent', 'H5_clipboard'],
        'bonus_score': 30,
        'auto_classify': 'MODERATE',
        'description': 'Multiple formatting artifacts suggesting external paste'
    }
}

def check_composite_patterns(detected_markers):
    """
    Check for composite patterns and apply bonus scores
    """
    triggered_composites = []
    
    for pattern_id, pattern in composite_patterns.items():
        if all(evaluate_condition(m, detected_markers) for m in pattern['required_markers']):
            triggered_composites.append({
                'pattern': pattern_id,
                'name': pattern['name'],
                'bonus': pattern['bonus_score'],
                'auto_classify': pattern['auto_classify'],
                'description': pattern['description']
            })
    
    return triggered_composites
```

### 17.2 Negative Patterns (Reduce Score)
Patterns that suggest human writing, reducing AI probability.

```python
human_indicators = {
    'TYPO_PATTERN': {
        'description': 'Presence of typos later corrected (Track Changes)',
        'score_reduction': 15,
        'rationale': 'AI rarely makes typos; human editors do'
    },
    
    'INCONSISTENT_STYLE': {
        'description': 'Natural variation in sentence structure and length',
        'score_reduction': 10,
        'rationale': 'Human writing shows natural variation'
    },
    
    'PERSONAL_VOICE': {
        'description': 'First-person perspective, personal anecdotes',
        'score_reduction': 20,
        'rationale': 'AI rarely uses genuine personal voice authentically'
    },
    
    'DOMAIN_EXPERTISE': {
        'description': 'Specific technical details, insider knowledge',
        'score_reduction': 15,
        'rationale': 'Deep domain expertise suggests human author'
    },
    
    'COLLOQUIALISMS': {
        'description': 'Natural contractions, informal expressions',
        'score_reduction': 10,
        'rationale': 'Casual language patterns suggest human writing'
    }
}
```

---

## 18. Machine Learning Enhancement (Future)

### 18.1 Feature Vector for ML Model
```python
def extract_ml_features(document, marker_results):
    """
    Extract feature vector for ML classification
    """
    features = {
        # Rule-based scores (10 categories)
        'score_A': marker_results['A'],
        'score_B': marker_results['B'],
        'score_C': marker_results['C'],
        'score_D': marker_results['D'],
        'score_E': marker_results['E'],
        'score_F': marker_results['F'],
        'score_G': marker_results['G'],
        'score_H': marker_results['H'],
        'score_I': marker_results['I'],
        'score_J': marker_results['J'],
        
        # Statistical features
        'word_count': document.word_count,
        'sentence_count': document.sentence_count,
        'avg_sentence_length': document.avg_sentence_length,
        'sentence_length_std': document.sentence_length_std,
        'avg_word_length': document.avg_word_length,
        'vocabulary_richness': document.unique_words / document.word_count,
        'paragraph_count': document.paragraph_count,
        'avg_paragraph_length': document.avg_paragraph_length,
        
        # Punctuation ratios
        'comma_ratio': document.comma_count / document.word_count,
        'period_ratio': document.period_count / document.word_count,
        'question_ratio': document.question_count / document.sentence_count,
        'exclamation_ratio': document.exclamation_count / document.sentence_count,
        
        # POS tag distributions
        'noun_ratio': document.pos_counts['NOUN'] / document.word_count,
        'verb_ratio': document.pos_counts['VERB'] / document.word_count,
        'adj_ratio': document.pos_counts['ADJ'] / document.word_count,
        'adv_ratio': document.pos_counts['ADV'] / document.word_count,
        
        # Readability scores
        'flesch_reading_ease': document.flesch_score,
        'gunning_fog_index': document.fog_index,
        
        # Composite pattern triggers
        'smoking_gun_count': len(marker_results['composite_triggers']),
        'human_indicator_count': len(marker_results['human_indicators'])
    }
    
    return features
```

### 18.2 Ensemble Approach
```python
class AWAREEnsemble:
    """
    Combine rule-based and ML approaches
    """
    def __init__(self, rule_weight=0.6, ml_weight=0.4):
        self.rule_weight = rule_weight
        self.ml_weight = ml_weight
        self.ml_model = load_model('aware_classifier.pkl')
    
    def predict(self, document):
        # Rule-based score
        rule_result = self.rule_based_analyze(document)
        rule_score = rule_result['adjusted_score']
        
        # ML score
        features = extract_ml_features(document, rule_result)
        ml_score = self.ml_model.predict_proba(features)[0][1] * 100
        
        # Ensemble
        final_score = (rule_score * self.rule_weight) + (ml_score * self.ml_weight)
        
        # Confidence based on agreement
        agreement = 1 - abs(rule_score - ml_score) / 100
        
        return {
            'rule_score': rule_score,
            'ml_score': ml_score,
            'ensemble_score': final_score,
            'model_agreement': agreement,
            'high_confidence': agreement > 0.8
        }
```

---

## 19. Integration Checklist

### 19.1 System Requirements
```
□ Python 3.9+
□ Required packages:
  - python-docx >= 0.8.11
  - spacy >= 3.0 (with en_core_web_sm model)
  - numpy >= 1.21
  - pandas >= 1.3
  - lxml >= 4.6
  - regex >= 2021.8
  
□ Optional (for ML enhancement):
  - scikit-learn >= 1.0
  - xgboost >= 1.5
  
□ Storage:
  - Document upload: 50MB max per file
  - Analysis results: ~10KB per analysis JSON
  
□ Performance targets:
  - Analysis time: <30 seconds for 10K word document
  - Concurrent analyses: 10+ simultaneous
```

### 19.2 Implementation Phases
```
Phase 1: Core Detection (MVP)
□ Categories A, B, D, E (text-based markers)
□ Basic scoring algorithm
□ Simple JSON output
□ Command-line interface
Timeline: 2 weeks

Phase 2: Enhanced Analysis
□ Categories C, F, G (comparative & structural)
□ Document annotation
□ Visual report generation
□ API endpoints
Timeline: 2 weeks

Phase 3: Advanced Features
□ Categories H, I, J (technical, academic, behavioral)
□ Composite pattern detection
□ Configurable thresholds
□ Admin dashboard
Timeline: 2 weeks

Phase 4: ML Integration
□ Feature extraction pipeline
□ Model training framework
□ Ensemble scoring
□ Continuous learning
Timeline: 3 weeks
```

---

## 20. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2025 | Initial specification (Categories A-D) |
| 2.0 | Jan 2025 | Extended specification (Categories E-J, composites, ML) |

---

*This specification is designed to be fed to Claude Code for system implementation. All patterns, weights, and thresholds are configurable parameters to allow for calibration and tuning based on real-world results.*
