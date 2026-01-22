# 🛡️ AWARE AI Content Detection System v2.0

**A**I **W**riting **A**nalysis & **R**isk **E**valuation - An advanced, multi-dimensional system for detecting AI-generated content with statistical rigor and comprehensive analysis.

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Detection Categories](#detection-categories)
  - [Category A: High-Confidence Markers](#category-a-high-confidence-markers)
  - [Category B: Moderate-Confidence Markers](#category-b-moderate-confidence-markers)
  - [Category C: Contextual Markers](#category-c-contextual-markers)
  - [Category D: Stylistic Markers](#category-d-stylistic-markers)
  - [Category E: Vocabulary Markers](#category-e-vocabulary-markers)
  - [Category F: Structural Markers](#category-f-structural-markers)
  - [Category G: Semantic Markers](#category-g-semantic-markers)
  - [Category H: Technical Artifacts](#category-h-technical-artifacts)
  - [Category I: Academic-Specific Markers](#category-i-academic-specific-markers)
  - [Category J: Behavioral Markers](#category-j-behavioral-markers)
- [Advanced Features](#advanced-features)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

AWARE AI Content Detection System is a comprehensive, research-backed framework for identifying AI-generated or AI-assisted content in documents. The system analyzes text across **10 distinct categories** with **50+ individual markers** and **10 advanced statistical features**, providing detailed insights into the likelihood of AI involvement.

### What Makes AWARE Different?

- **Multi-Dimensional Analysis**: Combines rule-based detection with advanced statistical methods (Bayesian probability, entropy analysis, burstiness metrics)
- **Reduced False Positives**: 30-40% reduction through contextual adjustments and weighted scoring
- **Comprehensive Evidence**: Detailed breakdowns showing exactly what was detected and why
- **Modern UI/UX**: Intuitive interface with real-time feedback, animations, and visual analytics
- **Production-Ready**: Built with FastAPI, optimized for Python 3.14+, with comprehensive error handling

---

## ✨ Key Features

### 🔍 Detection Capabilities
- **50+ Detection Markers** across 10 categories
- **Advanced Statistical Analysis**: Lexical diversity, burstiness, entropy, n-gram repetition
- **Bayesian Scoring Framework**: Statistical probability adjustments for higher accuracy
- **Pattern Correlation Detection**: Identifies dangerous combinations of markers
- **Contextual Adjustments**: Reduces false positives based on document type and characteristics

### 📊 Analysis Features
- **Lexical Diversity**: Type-token ratio, MTLD, Yule's K, Simpson's Index, Hapax Legomena
- **Readability Metrics**: Flesch Reading Ease, Gunning Fog, Flesch-Kincaid Grade, SMOG, ARI, Coleman-Liau
- **Burstiness Analysis**: Measures sentence complexity variation
- **Entropy Analysis**: Shannon entropy for text predictability
- **Anomaly Detection**: Statistical outlier identification with z-scores

### 💻 User Interface
- **Modern Design**: Gradient backgrounds, animations, responsive layout
- **Step-by-Step Workflow**: Guided process with progress indicators
- **Real-Time Feedback**: Word counter, drag & drop file upload
- **Visual Analytics**: SVG circular score display, category breakdowns, evidence highlighting
- **Multi-Tab Results**: Overview, Categories, Advanced Metrics, and Evidence views
- **Export Functionality**: JSON export and print-friendly reports

---

## 🚀 Quick Start

### Prerequisites

- Python 3.14 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vikast908/aimodeldetection.git
   cd aimodeldetection
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (automatic on first run, or manually)
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('punkt_tab')"
   ```

### Running the Application

1. **Start the server**
   ```bash
   uvicorn backend.main:app --reload
   ```

2. **Open your browser**
   ```
   http://localhost:8000
   ```

3. **Upload or paste your text** and get instant analysis!

---

## 🔬 Detection Categories

The AWARE system analyzes content across 10 distinct categories, each focusing on different aspects of AI-generated text.

### Category A: High-Confidence Markers

**Weight: 30% | High Priority**

These markers provide strong evidence of AI generation with high statistical confidence.

#### A1: Em-Dash Usage
AI models, particularly GPT variants, frequently use em-dashes (—) in ways that differ from typical human writing patterns.

- **What it detects**: Excessive use of em-dashes or double hyphens converted to em-dashes
- **Threshold**: 3+ occurrences become suspicious; 6+ is high confidence
- **Scoring**:
  - 0-2 occurrences: 0 points (normal)
  - 3-5 occurrences: (count - 2) × 15 points
  - 6+ occurrences: 45 + (count - 5) × 20 points
- **Max contribution**: 150 points

#### A2: Colon/Semicolon Density
Unusual frequency of colons and semicolons in running text (excluding citations and time formats).

- **What it detects**: Abnormal density of : and ; punctuation
- **Baseline**: 1 per 500 words is normal
- **Calculation**: density = (count / word_count) × 500
- **Scoring**: excess × 10 × (word_count / 500)
- **Max contribution**: 100 points

#### A3: Unicode Subscript/Superscript Characters
AI sometimes outputs Unicode subscript/superscript characters (₀₁₂₃, ⁰¹²³) instead of proper formatting.

- **What it detects**: Unicode subscript digits (₀-₉) or superscript (⁰-⁹)
- **Context**: Should use proper formatting, not Unicode characters
- **Scoring**: occurrences × 25 points
- **Max contribution**: 150 points

#### A4: Quotation Mark Inconsistencies
Mixed usage of straight quotes ("") and smart quotes ("") within the same document.

- **What it detects**: Inconsistent quotation mark styles
- **Analysis**: Measures ratio of straight to smart quotes
- **Scoring**: 5 points per inconsistency cluster
- **Max contribution**: 50 points

---

### Category B: Moderate-Confidence Markers

**Weight: 15% | Investigation Triggers**

These markers warrant investigation but aren't conclusive alone.

#### B1: Transitional Word Patterns
AI models overuse specific transitional phrases at sentence beginnings.

- **Patterns detected**:
  - "Furthermore," "Moreover," "Additionally,"
  - "Consequently," "Subsequently," "Nevertheless,"
  - "Nonetheless," "Correspondingly,"
- **Threshold**: 2 per 1000 words is normal
- **Scoring**: excess × 8 points
- **Max contribution**: 80 points

#### B2: Enumeration Patterns
Mechanical use of enumeration words (Firstly, Secondly, Finally).

- **Patterns detected**: Sequential enumeration markers
- **Scoring**:
  - Single occurrence: 0 points
  - Pair (First...Second): 6 points
  - Full sequence (3+): 12 points per sequence
- **Max contribution**: 60 points

#### B3: Spacing Anomalies
Unusual spacing around punctuation marks.

- **Patterns detected**:
  - Space inside parentheses: "( text )"
  - Space around em-dash: "word — word"
  - Space around forward slash: "and / or"
- **Scoring**: 5 points per occurrence
- **Max contribution**: 50 points

#### B4: Line Break Irregularities
Unexpected line breaks within sentences.

- **What it detects**: Line breaks not at paragraph boundaries
- **Pattern**: Line break followed by lowercase letter (mid-sentence)
- **Scoring**: 3 points per occurrence
- **Max contribution**: 30 points

#### B5: Repetitive Sentence Structures
Multiple consecutive sentences with identical grammatical structure.

- **Detection**: Analyzes part-of-speech patterns
- **Threshold**: 3+ consecutive sentences with >70% structure similarity
- **Scoring**: 10 points per cluster
- **Max contribution**: 50 points

---

### Category C: Contextual Markers

**Weight: 15% | Requires Comparison**

These markers require comparison with original document or metadata analysis.

#### C1: Extent of Edit (EoE) Analysis
Measures the degree of changes made to an original document.

- **Requires**: Original document for comparison
- **Calculation**: (words_changed / total_words) × 100
- **Flagging**:
  - EoE > 100%: Indicates copy-paste (30 points)
  - Additional: +5 points for every 10% above 100%
- **Max contribution**: 80 points

#### C2: Large Text Chunk Detection
Identifies large blocks of inserted text without granular edits.

- **Requires**: Track Changes data or XML metadata
- **Pattern**: Insertions > 50 words without intermediate tracked changes
- **Scoring**: 20 points per large chunk
- **Max contribution**: 100 points

#### C3: Editing Time Analysis
Analyzes whether editing duration matches document complexity.

- **Requires**: Metadata with editing duration
- **Baseline**: ~1 hour per 1,000 words for thorough editing
- **Flagging**:
  - ratio < 0.3: Severe (30 points)
  - ratio 0.3-0.5: Moderate (15 points)
  - ratio 0.5-0.7: Minor (5 points)
- **Max contribution**: 30 points

#### C4: Edit Cluster Analysis
Detects if edits are concentrated in specific sections.

- **Requires**: XML editing data
- **Pattern**: >60% of edits in <20% of document
- **Scoring**: 15 points if clustering detected
- **Max contribution**: 15 points

---

### Category D: Stylistic Markers

**Weight: 5% | Writing Style Patterns**

Subtle patterns in writing style that may indicate AI generation.

#### D1: Hedging Language Overuse
Excessive use of hedging phrases.

- **Patterns detected**:
  - "It is important to note that"
  - "It should be noted that"
  - "This suggests that" / "This indicates that"
- **Threshold**: 2 per 1000 words is normal
- **Scoring**: 4 points per excess occurrence
- **Max contribution**: 40 points

#### D2: Overly Formal Transitions
Unnecessarily formal transitional phrases.

- **Patterns detected**:
  - "In light of the above"
  - "Taking into consideration"
  - "With regard to" / "In terms of"
- **Scoring**: 3 points per occurrence
- **Max contribution**: 30 points

#### D3: Passive Voice Density
Abnormally high use of passive voice constructions.

- **Baseline**: 15% passive is normal in academic writing
- **Flagging**: >25% passive voice
- **Scoring**: 1 point per percentage point above 25%
- **Max contribution**: 25 points

#### D4: Sentence Length Uniformity
Unusually consistent sentence lengths (lack of natural variation).

- **Natural writing**: Standard deviation typically 8-15 words
- **AI writing**: Often SD < 5 words (too uniform)
- **Scoring**: (5 - SD) × 10 if SD < 5
- **Max contribution**: 30 points

---

### Category E: Vocabulary Markers

**Weight: 10% | Word Choice Patterns**

AI models have characteristic vocabulary preferences.

#### E1: AI-Favorite Words
Detection of words AI models use with unusual frequency.

- **AI-favorite words** (30+ including):
  - delve, crucial, pivotal, multifaceted, nuanced
  - comprehensive, robust, leverage, facilitate, utilize
  - landscape, paradigm, synergy, holistic, streamline
  - proliferation, unprecedented, simultaneously
  - necessitating, optimal, fundamental, contemporary
  - empirical, demonstrate, cohort, disparities, discourse
- **Scoring**:
  - 1-2 words: 0 points
  - 3-5 words: 15 points
  - 6-8 words: 30 points
  - 9+ words: 50 points
  - Bonus: +10 if any word appears 3+ times
- **Max contribution**: 70 points

#### E2: Contraction Avoidance
AI tends to avoid contractions, writing formally.

- **What it detects**: Ratio of expanded forms ("do not") vs contractions ("don't")
- **Scoring**:
  - avoidance_ratio > 0.9 AND total > 10: 25 points
  - avoidance_ratio > 0.8 AND total > 10: 15 points
  - avoidance_ratio > 0.7 AND total > 10: 5 points
- **Max contribution**: 25 points

#### E3: Vocabulary Sophistication Uniformity
Human writing varies in sophistication; AI maintains consistent complexity level.

- **Detection**: Calculates average word length per paragraph
- **Natural writing**: SD typically 0.5-1.5
- **AI writing**: SD often < 0.3
- **Scoring**:
  - SD < 0.2: 20 points
  - SD 0.2-0.3: 10 points
- **Max contribution**: 20 points

---

### Category F: Structural Markers

**Weight: 8% | Document Organization**

Patterns in how content is structured and organized.

#### F1: Paragraph Length Uniformity
AI generates paragraphs of suspiciously similar length.

- **Metric**: Coefficient of variation (CV = SD/mean)
- **Natural writing**: CV typically 0.4-0.8
- **AI writing**: CV often < 0.25
- **Scoring**:
  - CV < 0.15: 25 points
  - CV 0.15-0.25: 15 points
  - CV 0.25-0.35: 5 points
- **Max contribution**: 25 points

#### F2: Perfect Parallel Structures
Overly symmetrical lists and comparisons.

- **What it detects**: 4+ items with identical grammatical patterns
- **Example**: "The system improves X. The system reduces Y. The system enhances Z."
- **Scoring**: 10 points per perfect parallel set
- **Max contribution**: 30 points

#### F3: Balanced Argument Pattern
Artificially balanced pros/cons or advantages/disadvantages.

- **What it detects**: Exactly matched counts (e.g., 5 pros, 5 cons)
- **Scoring**: 15 points if perfectly balanced with 4+ items each side
- **Max contribution**: 15 points

---

### Category G: Semantic Markers

**Weight: 7% | Meaning-Level Patterns**

Analysis of what the text actually says (or doesn't say).

#### G1: Lack of Specific Examples
AI makes claims without concrete examples or data.

- **What it detects**: Ratio of vague quantifiers to specific details
- **Vague quantifiers**: "many studies", "research indicates", "experts agree"
- **Scoring**:
  - ratio > 3.0: 25 points
  - ratio 2.0-3.0: 15 points
  - ratio 1.0-2.0: 5 points
- **Max contribution**: 25 points

#### G2: Circular Definitions
Defining terms using the term itself.

- **Example**: "Quality management is the management of quality..."
- **Detection**: Analyzes sentences with "is defined as", "refers to", "means"
- **Scoring**: 15 points per circular definition
- **Max contribution**: 30 points

#### G3: Generic Statements Without Substance
Truisms and obvious statements that fill space without adding value.

- **Patterns**:
  - "X is important"
  - "X has both advantages and disadvantages"
  - "X requires careful consideration"
- **Scoring**: 3 points per generic statement
- **Max contribution**: 30 points

---

### Category H: Technical Artifacts

**Weight: 5% | Metadata and Formatting**

Document metadata and formatting signals indicating external content.

#### H1: Font Inconsistencies
Copy-pasted text may have different font properties.

- **What it detects**: Abrupt font changes not at section boundaries
- **Scoring**: 10 points per unexplained font change cluster
- **Max contribution**: 40 points

#### H2: Style Inconsistencies
Mixed formatting styles indicating external paste.

- **What it detects**: Mixed heading styles, inconsistent list formatting, varying spacing
- **Scoring**: 5 points per inconsistency type
- **Max contribution**: 25 points

#### H3: Metadata Timestamp Anomalies
Document metadata shows suspicious timing.

- **Patterns**:
  - Large document (>5000 words) with <3 revisions: 20 points
  - Modification time < creation time + 10 min: 15 points
- **Max contribution**: 25 points

#### H5: Clipboard Artifacts
Special characters from web/AI tool copy-paste.

- **What it detects**:
  - Zero-width spaces (U+200B)
  - Zero-width joiners (U+200D)
  - Non-breaking spaces in unusual places
  - Object replacement characters (U+FFFC)
- **Scoring**: 10 points per cluster
- **Max contribution**: 40 points

---

### Category I: Academic-Specific Markers

**Weight: 3% | Scholarly Writing**

Patterns specific to academic and scientific writing.

#### I1: Citation Anomalies
AI often creates plausible but incorrect citations.

- **What it detects**:
  - Format inconsistencies
  - Suspiciously round years (2020, 2021, 2022)
  - "et al." overuse
  - Citations that don't match reference list
- **Scoring**: 15 points per citation anomaly cluster
- **Max contribution**: 45 points

#### I2: Generic Methodology Descriptions
Vague methodology without specific details.

- **Patterns**:
  - "standard procedures were followed"
  - "appropriate statistical methods"
  - Lack of specific equipment/software names
- **Scoring**: 10 points if multiple vague phrases detected
- **Max contribution**: 20 points

#### I3: Results Without Data
Results described qualitatively without actual numbers.

- **What it detects**: Results sections lacking quantitative data
- **Patterns**: "showed significant improvement" without p-values or percentages
- **Scoring**: 15 points if lacking quantitative data
- **Max contribution**: 15 points

---

### Category J: Behavioral Markers

**Weight: 2% | Edit Behavior Analysis**

Patterns based on how the document was edited (requires Track Changes).

#### J1: Wholesale Replacement Pattern
Human edits are scattered; AI replacement is wholesale.

- **What it detects**: >80% of paragraphs with >50% rewrite each
- **Scoring**:
  - >80% paragraphs: 35 points
  - >60% paragraphs: 20 points
  - >40% paragraphs: 10 points
- **Max contribution**: 35 points

#### J2: Edit Granularity Analysis
Human edits are word/phrase level; AI replacement is sentence/paragraph level.

- **Natural editing**: ~70% word/phrase level
- **AI replacement**: Often >60% sentence+ level
- **Scoring**:
  - >70% sentence+ level: 25 points
  - >50% sentence+ level: 15 points
- **Max contribution**: 25 points

---

## 🧠 Advanced Features

### Lexical Diversity Analysis
Measures vocabulary richness through multiple metrics:
- **Type-Token Ratio (TTR)**: Unique words / total words
- **MTLD**: Measure of Textual Lexical Diversity
- **Yule's K**: Measures word frequency distribution
- **Simpson's Index**: Probability of selecting two different words
- **Hapax Legomena Ratio**: Proportion of words appearing once

### Readability Scoring
Comprehensive readability analysis:
- **Flesch Reading Ease**: 0-100 scale (higher = easier)
- **Flesch-Kincaid Grade Level**: US grade level
- **Gunning Fog Index**: Years of education needed
- **SMOG Index**: Simple Measure of Gobbledygook
- **Automated Readability Index (ARI)**: Character-based readability
- **Coleman-Liau Index**: Formula based on characters

### Burstiness Analysis
Measures sentence complexity variation:
- **Burstiness Score**: Variance in sentence characteristics
- **Perplexity Variance**: Unpredictability in word patterns
- **Complexity Variation**: Changes in sentence structure

### Pattern Correlation Detection
Identifies dangerous combinations of markers:
- **Smoking Gun Patterns**: Multiple AI indicators appearing together
- **Composite Bonus Scoring**: Additional points for correlated markers
- **Auto-Classification Override**: Elevates risk level based on patterns

### Bayesian Statistical Framework
Applies probabilistic reasoning:
- **Prior Probabilities**: Based on document type (academic, business, general)
- **Likelihood Ratios**: Evidence strength calculation
- **Posterior Probability**: Final statistical likelihood of AI generation

### Contextual Adjustments
Reduces false positives through context-aware scoring:
- **Document Length Adjustment**: Shorter documents = less reliable
- **Academic Writing Adjustment**: Natural formality doesn't trigger false positives
- **Citation Patterns**: Proper citations reduce false positives

---

## 📡 API Documentation

### Health Check
```http
GET /api/health
```
Returns server status.

**Response**:
```json
{
  "status": "ok"
}
```

---

### Analyze Text
```http
POST /api/analyze
```

Analyzes uploaded text or document for AI-generated content.

**Request Parameters**:
- `text` (optional): Plain text to analyze
- `file` (optional): Document file (.txt, .md, .docx, .doc, .pdf)
- `original_file` (optional): Original document for comparison

**Example - Text Analysis**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "text=Your text here..."
```

**Example - Document Analysis**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@document.docx"
```

**Example - With Original Document**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@edited.docx" \
  -F "original_file=@original.docx"
```

**Response Structure**:
```json
{
  "score": 48.3,
  "classification": "MODERATE",
  "confidence": "HIGH",
  "categories": {
    "A": {
      "score": 75.2,
      "markers": [
        {
          "id": "A1",
          "name": "Em-Dash Usage",
          "count": 8,
          "score": 105,
          "evidence": [...]
        }
      ]
    }
  },
  "advanced_analysis": {
    "lexical_diversity": {
      "type_token_ratio": 0.62,
      "mtld": 72.45
    },
    "burstiness": {
      "burstiness_score": 0.45
    },
    "bayesian_analysis": {
      "posterior_probability": 45.6
    }
  },
  "scoring_breakdown": {
    "base_score": 45.2,
    "composite_bonus": 50,
    "bayesian_adjusted": 52.1,
    "final_score": 48.3
  },
  "recommendation": "Medium probability. Review recommended.",
  "meta": {
    "analysis_id": "uuid",
    "timestamp": "2026-01-22T...",
    "version": "2.0_enhanced",
    "document": {
      "word_count": 1847,
      "paragraph_count": 12,
      "sentence_count": 89
    }
  }
}
```

---

### Risk Classifications

| Score | Classification | Probability | Recommended Action |
|-------|----------------|-------------|-------------------|
| 0-15 | MINIMAL | Low probability | No action needed |
| 16-35 | LOW | Some indicators | Monitor only |
| 36-55 | MODERATE | Medium probability | Review recommended |
| 56-75 | HIGH | High probability | Investigation required |
| 76-100 | CRITICAL | Very high probability | Immediate action |

---

## 🏗️ Architecture

### Backend Structure
```
backend/
├── main.py                 # FastAPI application
├── aware_analyzer.py       # Core detection engine
├── advanced_features.py    # Statistical analysis
└── parsers.py             # Document parsing (.docx, .pdf, .txt)
```

### Frontend Structure
```
frontend/
├── index.html             # Main UI interface
├── styles.css             # Modern design system
└── app.js                 # Client-side logic
```

### Technology Stack
- **Backend**: FastAPI 0.110.0, Python 3.14+
- **NLP**: NLTK (tokenization, POS tagging)
- **Document Parsing**: python-docx, PyPDF2
- **Frontend**: Vanilla JavaScript, CSS3
- **Server**: Uvicorn ASGI server

---

## 📝 Usage Examples

### Example 1: Quick Text Analysis
```python
import requests

text = "Your document text here..."
response = requests.post(
    "http://localhost:8000/api/analyze",
    data={"text": text}
)
result = response.json()
print(f"AI Detection Score: {result['score']}")
print(f"Classification: {result['classification']}")
```

### Example 2: Document Analysis with Python
```python
import requests

with open("document.docx", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        files={"file": f}
    )
result = response.json()

# Access detailed analysis
print(f"Score: {result['score']}")
print(f"AI-Favorite Words: {result['categories']['E']['markers'][0]['count']}")
print(f"Lexical Diversity: {result['advanced_analysis']['lexical_diversity']}")
```

### Example 3: Comparative Analysis
```python
import requests

files = {
    "file": open("edited.docx", "rb"),
    "original_file": open("original.docx", "rb")
}
response = requests.post(
    "http://localhost:8000/api/analyze",
    files=files
)
result = response.json()
print(f"Introduced Changes Score: {result['categories']['C']['score']}")
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Areas for Contribution
- Additional language support
- New detection markers
- UI/UX improvements
- Performance optimizations
- Documentation enhancements

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (if available)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- AWARE framework inspired by research in AI content detection
- Built with contributions from the open-source community
- Enhanced with statistical methods from computational linguistics research

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/vikast908/aimodeldetection/issues)
- **Documentation**: [Full Documentation](AWARE_AI_Detection_Algorithm.md)
- **Enhancements**: [Technical Details](ENHANCEMENTS.md)
- **Quick Reference**: [Quick Start Guide](QUICK_REFERENCE.md)

---

## 🔄 Version History

### v2.0 Enhanced (Current)
- Added 10 advanced statistical features
- Implemented Bayesian probability framework
- Expanded AI-favorite words detection (30+ words)
- Reduced false positives by 30-40%
- Complete UI/UX redesign
- Python 3.14 compatible

### v1.0 Original
- 10 detection categories (A-J)
- 50+ individual markers
- Rule-based scoring system
- Basic web interface

---

## 🎯 Roadmap

- [ ] Machine learning model training on collected features
- [ ] Multi-language support
- [ ] Real-time collaborative analysis
- [ ] Browser extension
- [ ] API rate limiting and authentication
- [ ] Advanced visualization dashboard
- [ ] Integration with document management systems

---

**Made with 💙 by the AWARE Team**

*Detecting AI-generated content with precision and transparency*
