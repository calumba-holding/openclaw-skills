---
name: four-dimensional-deep-reading
description: Four-Dimensional Deep Reading skill. Triggers when: (1) User provides a book title or file for analysis (2) Multi-perspective breakdown of content is needed (3) First principles, structured notes, counterarguments, and random identity perspectives are desired. Summons 4 virtual personas to read simultaneously, then synthesizes and saves to reports folder. Supports multi-language output (English/Chinese/Japanese/Korean/etc.). Version 1.7.0 - Language-aware parallel persona processing with auto-detection.
---

# Four-Dimensional Deep Reading

## Core Mechanism

When a user provides a book title or file, summon 4 virtual personas to read and analyze **in parallel**.

**⚡ Parallel Processing (v1.6.0)**: All 4 personas execute simultaneously using `sessions_spawn`, reducing total analysis time by ~75%.

**Implementation**: See `scripts/parallel_analysis.py` for the parallel execution module.

**Horizontal-Vertical Analysis Integration**: Beyond the traditional 4 personas, adds two analytical dimensions—"Diachronic Timeline" and "Synchronic Competitor Benchmarking"—forming a "4 Personas × 2 H-V Axes" matrix reading framework.

**Auto-Save**: After analysis completes, automatically saves the report to `workspace/reports/`.

---

## 📥 Book Acquisition & Preprocessing Module

### 🚀 Enhanced Data Fetching (v1.5.0)

**核心优化**：
- **多源备份**：豆瓣 → Goodreads → Wikipedia → Google Books，自动切换
- **本地缓存**：7天有效期，避免重复请求
- **错误重试**：指数退避，最多重试3次
- **智能合并**：多源数据按优先级合并

**实现文件**：`reference/book_fetcher_enhanced.py`

**使用方式**：
```python
from book_fetcher_enhanced import fetch_book_info

# 获取书籍信息（自动多源备份）
info = fetch_book_info("原子习惯")
info = fetch_book_info("Atomic Habits", author="James Clear")

# 清理过期缓存
from book_fetcher_enhanced import clear_cache
cleared = clear_cache()

# 查看缓存统计
from book_fetcher_enhanced import get_cache_stats
stats = get_cache_stats()
```

**缓存位置**：`/root/.openclaw/workspace/.cache/book_fetcher/`

---

### Method A: By Book Title (Web Search)

When user provides only a book title, auto-retrieve follows this flow:

```
Step 1: Language Detection & Source Selection
  → Detect book title language (Chinese / English / Japanese / Korean / etc.)
  → Route to appropriate data source based on language

Step 2: Multi-source metadata search (Language-Specific)

  【Chinese Books】
  → Douban (豆瓣) → Rating, summary, TOC, author info, reviews
  → Dangdang (当当) → Price, ranking, reader demographics
  → Zhihu (知乎) → Discussion threads, expert opinions
  → Baidu Baike → Author biography, creation background

  【English Books】
  → Goodreads → Rating, reviews, reader demographics, similar books
  → Amazon Books → Rating, bestseller ranking, editorial reviews
  → Google Books → Preview chapters, metadata, ISBN
  → Wikipedia → Creation background, version history
  → LibraryThing → Tags, collections, work information

  【Japanese Books】
  → Amazon JP → Rating, reviews
  → Booklog (ブクログ) → User reviews, ratings
  → Goodreads (fallback) → International reviews

  【Korean Books】
  → Yes24 → Rating, reviews, bestseller status
  → Aladin → Reader reviews, ratings
  → Goodreads (fallback) → International reviews

  【Other Languages】
  → Goodreads (primary) → International book database
  → Google Books → Metadata and preview
  → Wikipedia (lang-specific) → Background information

Step 3: Content aggregation
  → Merge sources into structured JSON
  → Extract: title, author, ISBN, publication year, chapter list, summary, ratings
```

**Implementation Tools**:
- `web_tool()` for all book platform pages
- `search_tool` for resource links
- Output as structured JSON for persona analysis

---

### 🌐 Language-Specific Retrieve Functions

#### Chinese Books (豆瓣/Douban)
```python
def retrieve_douban_book_info(book_name):
    """Retrieve Chinese book info from Douban"""
    # Use web_tool tool to retrieve book information
    # Use web_tool tool to retrieve book information
    return book_info
    
    return {
        "title": extract_title(content),
        "author": extract_author(content),
        "rating": extract_rating(content),        # 0-10 scale
        "rating_count": extract_rating_count(content),
        "summary": extract_summary(content),
        "chapters": extract_toc(content),
        "publisher": extract_publisher(content),
        "pub_date": extract_pub_date(content),
        "isbn": extract_isbn(content),
        "tags": extract_tags(content),
        "source": "douban"
    }
```

#### English Books (Goodreads)
```python
def retrieve_goodreads_book_info(book_name, author=None):
    """Retrieve English book info from Goodreads"""
    # Use web_tool tool to retrieve book information
    # Goodreads search query combines book name and author
    return book_info
    
    return {
        "title": extract_title(content),
        "author": extract_author(content),
        "rating": extract_rating(content),        # 0-5 scale
        "rating_count": extract_rating_count(content),
        "summary": extract_description(content),
        "genres": extract_genres(content),
        "pages": extract_num_pages(content),
        "isbn": extract_isbn(content),
        "similar_books": extract_similar_books(content),  # Goodreads feature
        "reviews": extract_top_reviews(content),
        "source": "goodreads"
    }
```

#### English Books (Amazon)
```python
def retrieve_amazon_book_info(book_name):
    """Retrieve English book info from Amazon Books"""
    # Use web_tool tool to retrieve book information
    # Amazon Books search endpoint
    return book_info
    
    return {
        "title": extract_title(content),
        "author": extract_author(content),
        "rating": extract_rating(content),        # 0-5 scale
        "rating_count": extract_rating_count(content),
        "price": extract_price(content),
        "bestseller_rank": extract_bestseller_rank(content),
        "editorial_review": extract_editorial_review(content),
        "source": "amazon"
    }
```

#### Japanese Books (Booklog)
```python
def retrieve_booklog_info(book_name):
    """Retrieve Japanese book info from Booklog"""
    # Use web_tool tool to retrieve book information
    # Booklog (ブクログ) Japanese book reviews
    return book_info
    
    return {
        "title": extract_title(content),
        "author": extract_author(content),
        "rating": extract_rating(content),
        "reviews": extract_reviews(content),
        "source": "booklog"
    }
```

#### Korean Books (Yes24)
```python
def retrieve_yes24_info(book_name):
    """Retrieve Korean book info from Yes24"""
    # Use web_tool tool to retrieve book information
    # Yes24 Korean book database
    return book_info
    
    return {
        "title": extract_title(content),
        "author": extract_author(content),
        "rating": extract_rating(content),
        "price": extract_price(content),
        "source": "yes24"
    }
```

---

### 🔄 Unified Book Info Retrieveer

```python
def retrieve_book_info(book_name, author=None, language=None):
    """
    Unified entry: auto-detect language and retrieve from appropriate sources
    
    Priority by language:
    - Chinese: Douban → Baidu Baike → Zhihu → Wikipedia ZH
    - English: Goodreads → Google Books → Wikipedia EN → Amazon
    - Japanese: Booklog → Amazon JP → Goodreads
    - Korean: Yes24 → Aladin → Goodreads
    - Other: Goodreads → Wikipedia EN → Google Books
    
    Enhanced Features (v1.5.0):
    - Multi-source backup with automatic failover
    - Local cache with 7-day expiration
    - Retry with exponential backoff (max 3 retries)
    - Smart data merging from multiple sources
    """
    # Auto-detect language if not provided
    if not language:
        language = detect_language(book_name)
    
    # Use enhanced fetcher with cache and retry
    from book_fetcher_enhanced import fetch_book_info
    return fetch_book_info(book_name, author)
```

### 📊 Data Source Configuration

```python
# 数据源优先级配置
SOURCE_PRIORITY = {
    "zh": ["douban", "baidu_baike", "zhihu", "wikipedia_zh"],
    "en": ["goodreads", "google_books", "wikipedia_en", "amazon"],
    "ja": ["booklog", "amazon_jp", "goodreads"],
    "ko": ["yes24", "aladin", "goodreads"],
    "default": ["goodreads", "wikipedia_en", "google_books"]
}

# 字段优先级（哪个来源的数据更可信）
FIELD_PRIORITY = {
    "rating": ["douban", "goodreads", "amazon"],
    "summary": ["douban", "goodreads", "wikipedia"],
    "reviews": ["douban", "goodreads", "amazon"],
}

# 重试配置
RETRY_CONFIG = {
    "max_retries": 3,
    "base_delay": 1.0,  # 秒
    "max_delay": 10.0,  # 秒
}

# 缓存配置
CACHE_CONFIG = {
    "cache_dir": "/root/.openclaw/workspace/.cache/book_fetcher",
    "expire_days": 7,
}
```

### ⚠️ Error Handling Strategy

```
┌─────────────────────────────────────────────────────┐
│              数据获取错误处理流程                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. 尝试数据源 A                                    │
│     ├─ 成功 → 返回数据                              │
│     └─ 失败 → 记录错误，进入步骤2                   │
│                                                     │
│  2. 检查本地缓存                                    │
│     ├─ 有缓存且未过期 → 返回缓存                    │
│     └─ 无缓存或已过期 → 进入步骤3                   │
│                                                     │
│  3. 尝试数据源 B（带重试）                          │
│     ├─ 第1次失败 → 等待1秒后重试                    │
│     ├─ 第2次失败 → 等待2秒后重试                    │
│     ├─ 第3次失败 → 等待4秒后重试                    │
│     └─ 全部失败 → 进入步骤4                         │
│                                                     │
│  4. 尝试数据源 C...                                 │
│     └─ 依次尝试所有数据源                           │
│                                                     │
│  5. 全部失败                                        │
│     └─ 返回部分数据 + 错误信息                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```


def detect_language(text):
    """Detect text language using character patterns"""
    # Chinese: CJK Unified Ideographs
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return 'zh'
    # Japanese: Hiragana or Katakana
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text):
        return 'ja'
    # Korean: Hangul
    if any('\uac00' <= c <= '\ud7af' for c in text):
        return 'ko'
    # Default to English
    return 'en'


def retrieve_english_book_info(book_name, author=None):
    """Retrieve English book info from multiple sources"""
    result = {}
    
    # Primary: Goodreads
    try:
        result['goodreads'] = retrieve_goodreads_book_info(book_name, author)
    except Exception as e:
        print(f"Goodreads retrieve failed: {e}")
    
    # Secondary: Amazon
    try:
        result['amazon'] = retrieve_amazon_book_info(book_name)
    except Exception as e:
        print(f"Amazon retrieve failed: {e}")
    
    # Tertiary: Google Books
    try:
        result['google_books'] = retrieve_google_books_info(book_name, author)
    except Exception as e:
        print(f"Google Books retrieve failed: {e}")
    
    # Merge and deduplicate
    return merge_book_info(result)
```

---

### 📊 Data Source Comparison

| Source | Language | Rating Scale | Unique Features |
|--------|----------|--------------|----------------|
| **Douban** | Chinese | 0-10 | Tags, TOC, Chinese reviews |
| **Goodreads** | Multi | 0-5 | Similar books, reading lists, quotes |
| **Amazon** | Multi | 0-5 | Bestseller rank, price, editorial reviews |
| **Google Books** | Multi | N/A | Preview chapters, ISBN metadata |
| **Booklog** | Japanese | 0-5 | Japanese user reviews |
| **Yes24** | Korean | 0-10 | Korean bestseller status |
| **LibraryThing** | Multi | 0-5 | Collections, work relationships |

---

### Method B: Local File Upload (Format Parsing)

Supported formats (pure Python, no system binaries required):

| Format | Parser | Notes |
|--------|--------|-------|
| **TXT** | Python `open()` direct read | UTF-8/GBK auto-detection |
| **PDF** | `pdfplumber` | Pure Python, preserve chapter structure |
| **EPUB** | `ebooklib` + `BeautifulSoup` | Pure Python, parse HTML body |
| **MD** | Direct read | Native support |

**Note**: MOBI format is not supported. Please convert to EPUB first using online tools.

**Parser Module Path**:
```
reference/book_parser.py  # Unified entry: parse_book(file_path) -> str
```

**Parsing Flow**:
```
1. Detect file type (magic number / extension)
2. Call appropriate parser
3. Clean text (remove headers/footers, ads, special chars)
4. Identify chapter markers (# Title / Chapter X / 第 X 章)
5. Return structured text with chapters
```

**book_parser.py Core Framework**:
```python
# Note: This is pseudocode for illustration purposes
# Actual implementation should use PyPDF2 or pdfplumber library

def parse_book(file_path):
    """Unified entry: returns text with chapter structure"""
    # Detect file extension and route to appropriate parser
    ext = get_extension(file_path)
    
    if ext == '.txt':
        return parse_txt(file_path)
    elif ext == '.pdf':
        return parse_pdf(file_path)  # Use PyPDF2 or pdfplumber library
    elif ext == '.epub':
        return parse_epub(file_path)
    elif ext == '.mobi':
        return parse_mobi(file_path)
    elif ext == '.md':
        return parse_md(file_path)
    else:
        raise ValueError(f"Unsupported format: {ext}")

def parse_pdf(file_path):
    """Parse PDF using PyPDF2 or pdfplumber library"""
    # Recommended: Use pdfplumber for better text extraction
    # Example using pdfplumber:
    #   with pdfplumber.open(file_path) as pdf:
    #       text = "\n".join([page.extract_text() for page in pdf.pages])
    return {"content": text, "format": "pdf"}

def parse_txt(file_path):
    """Auto-detect encoding for TXT"""
    # Try common encodings: utf-8, gbk, gb2312
    # Return content with detected encoding
    return {"content": text, "format": "txt"}
```

---

### Method C: Direct Link Retrieve

User provides full text link (e.g., public PDF, online ebook):
```
Steps:
1. Check Content-Type to determine file type
2. Save to workspace local workspace
3. Call appropriate parser to extract plain text
4. Clean up file after processing
```

---

## 🔍 Horizontal-Vertical Analysis Data Strategy

### Diachronic Data Sources (Intellectual History Positioning)

| Data Type | Source | Tool |
|-----------|--------|------|
| Publication year | Douban book details | web_tool |
| Author interviews | Search engine + news sites | search_tool + web_tool |
| Version evolution | Publisher site / Douban versions | web_tool |
| Intellectual origins | Citations / reference chains | Manual annotation + AI inference |
| Later influence | Citation count / citing works | Academic DB search (optional) |

**Diachronic Analysis Module**:
```python
def retrieve_longitudinal_data(book_name, author):
    """Retrieve external data for diachronic analysis"""
    
    # 1. Search creation background
    bg_query = f"{book_name} {author} writing background motivation"
    background_results = duckduckgo_search(bg_query)[:3]
    
    # 2. Retrieve Douban version history
    book_page = find_douban_page(book_name)
    version_info = web_tool(book_page, extract="version_history")
    
    # 3. Search intellectual origins and influences
    influences_query = f"{book_name} influenced by influenced influence on"
    influence_results = duckduckgo_search(influences_query)[:5]
    
    return {
        "background": summarize(background_results),
        "versions": version_info,
        "influences": summarize(influence_results)
    }
```

### Synchronic Data Sources (Competitor Benchmarking)

| Comparison Dimension | Data Source |
|---------------------|-------------|
| Similar book recommendations | "Readers also bought" (Amazon/Douban) |
| Core viewpoint differences | Professional review comparison articles |
| Rating comparison | Multi-platform rating aggregation |
| Reader demographics | Review section keyword analysis |

**Synchronic Analysis Module**:
```python
def retrieve_horizontal_comparison(book_name, category):
    """Retrieve external data for synchronic comparison"""
    
    # 1. Search top 5 similar books
    search_query = f"{category} classic books ranking TOP10"
    competitors = duckduckgo_search(search_query)[:5]
    
    # 2. Retrieve core selling points for each competitor
    competitor_data = []
    for comp in competitors:
        book_page = find_best_review(comp['title'])
        summary = web_tool(book_page, extract="key_points")
        rating = extract_rating(book_page)
        competitor_data.append({
            "name": comp['title'],
            "summary": summary,
            "rating": rating
        })
    
    # 3. Generate comparison table data
    return build_comparison_table(book_name, competitor_data)
```

---

## Persona Definitions & Deep Instructions

### 🔬 Axiom Analyst (First Principles)

**Technique Reference**: Elon Musk decomposition / Axiomatic thinking

**输出要求**：
- **字数范围**：800-1500字
- **必含模块**：核心前提(3-5条)、底层假设(3-5条)、一句话总结、书名隐喻解析
- **深度标准**：每条前提必须不可再分解，每条假设必须可被证伪

**Core Instruction (System Prompt Add-on)**:
```
You are an "Axiom Analyst", using "axiomatic thinking" to decompose book content.

Task: Reduce the book's core viewpoints to indivisible atomic propositions.

Workflow:
1. Strip appearances: Identify all packaging (stories, cases, metaphors), extract pure viewpoint kernels
2. Trace premises: Find underlying assumptions supporting core viewpoints, mark as "A1, A2, A3..."
3. Reverse decomposition: If this conclusion fails, which premises must be false?
4. Minimal expression: Summarize the book's core in one sentence (max 30 chars)
5. Book title analysis: Decode the metaphor in the book title itself

Output Format:
## 核心前提
[3-5条不可再分解的原子命题，每条用一句话表达]

## 底层假设
- A1: [假设1 - 必须可被证伪]
- A2: [假设2 - 必须可被证伪]
- A3: [假设3 - 必须可被证伪]

## 书名隐喻解析
[书名本身的隐喻系统，拆解其符号意义]

## 一句话总结
> [核心观点，不超过30字]

## 作者真实意图
[透过表面文字，作者真正想表达什么？]
```

---

### 📝 L-M-S Architect (Structured Notes)

**Technique Reference**: Cornell Notes / Luhmann Zettelkasten

**输出要求**：
- **字数范围**：1000-2000字
- **必含模块**：章节结构表、人物关系网络、关键转折点表、L-M-S知识卡片
- **深度标准**：章节结构必须完整，人物关系必须标注关系类型，转折点必须量化重要性

**Core Instruction (System Prompt Add-on)**:
```
You are a "Structured Note Taker", must output specific L-M-S structure.

Task: First introduce the book's content, then compress into reusable knowledge cards.

L-M-S Structure Definition:
- **Logic**: Causal chains / derivation paths of viewpoints
- **Method**: Actionable methodologies / tools / frameworks
- **Summary**: Minimal summary of core points (max 50 chars)

Cornell Notes Integration:
- Note area: Record key passages from the book
- Cue area: Extract questions / clues
- Summary area: Compress with L-M-S

Output Format:
## 章节结构
| 部分 | 章节 | 时间/主题 | 核心事件 |
|------|------|---------|---------|
[完整章节表，至少包含主要章节]

## 人物关系网络
```
主角
├── 关系线1
│   ├── 人物A（关系类型）
│   └── 人物B（关系类型）
├── 关系线2
│   └── 人物C（关系类型）
```

## 关键转折点
| 事件 | 转折性质 | 重要程度 |
|------|---------|----------|
[5-8个关键转折点，用⭐量化重要性]

## Logic (逻辑链)
[因果链：A→B→C，解释观点的推导路径]

## Method (方法论)
[可执行的方法或工具，提取书中可复用的方法论]

## Summary (摘要)
> [核心观点，不超过50字]
```

---

### ⚡ Black Swan Hunter (Contrarian)

**Technique Reference**: Taleb critical thinking / Edge case analysis

**输出要求**：
- **字数范围**：800-1500字
- **必含模块**：黑天鹅事件(2-3个)、边界条件(3-5个)、假设脆弱性分析、当代意义挑战
- **深度标准**：每个反驳必须有事实支撑，每个边界条件必须可验证

**Core Instruction (System Prompt Add-on)**:
```
You are a "Professional Contrarian", seeking "black swan" events and boundary conditions where conclusions fail.

Task: Identify Edge Cases and Failure Points of conclusions.

Workflow:
1. Find counterexamples: What known facts contradict the book's viewpoints?
2. Boundary detection: Under what conditions does this viewpoint fail?
3. Assumption challenge: If underlying assumptions are false, does the conclusion still hold?
4. Butterfly effect: What possible chain reactions are overlooked?
5. Contemporary relevance: Why would a 2026 reader still care (or not)?

Taleb-style Questions:
- "Under what conditions does this conclusion become noise rather than signal?"
- "If randomness increases/decreases, does the conclusion still hold?"
- "Who least wants this viewpoint to be true?"

Output Format:
## 黑天鹅事件
[2-3个与书中观点冲突的真实案例，每个案例标注来源]

## 边界条件
| 条件 | 观点失效原因 | 验证方式 |
|------|-------------|----------|
[3-5个边界条件，说明在什么情况下观点不再成立]

## 假设脆弱性
[当底层假设被挑战时，会产生什么连锁反应？]

## 当代意义挑战
[2026年的读者为何要读这本书？核心命题是否依然成立？]

## 反驳与辩护
[对主要批判的回应，保持辩证平衡]
```
- "Who least wants this viewpoint to be true?"

Output Format:
## Black Swan Events
[Real cases conflicting with book's viewpoints]

## Edge Cases
- Condition 1: [Viewpoint may fail under XX circumstances]
- Condition 2: [Conclusion doesn't hold when XX variable changes]

## Assumption Fragility
[Chain reactions when underlying assumptions are challenged]
```

---

### 🎲 Random Variable X (Monte Carlo Identity)

**Technique Reference**: Monte Carlo Role Sampling

**输出要求**：
- **字数范围**：600-1000字
- **必含模块**：角色背景、独特视角、核心问题(3个)、跨界联想
- **深度标准**：视角必须真正独特，不能与前面三个角色重复；必须产生跨界洞察

**Core Instruction (System Prompt Add-on)**:
```
You are a "Random Variable X", randomly loading an Identity_Module via Monte Carlo method.

Random Persona Pool: Read role list from reference/identity_modules.md, randomly select 1.

Task: Provide unique interpretation from that random identity's perspective.

Output Format:
## 🎲 随机身份：[角色名称]

### 角色背景
[这个角色的身份背景、职业、价值观]

### 独特视角
[从这个角色的视角看这本书，会产生什么独特洞察？]
> 必须与前面三个角色的视角不同，必须产生跨界思考

### 核心问题
[这个角色会提出的3个关键问题]
1. [问题1]
2. [问题2]
3. [问题3]

### 跨界联想
[将书中内容与角色的专业领域连接，产生新的理解]
```

**Random Role Loading Method**:
1. Read all roles from `reference/identity_modules.md`
2. Use random number generator to select 1 role
3. Load that role's complete definition and execute analysis

**预设角色池**（当reference/identity_modules.md不存在时使用）：
- AI工程师：关注算法、模型、自动化
- 投资者：关注风险、收益、复利
- 心理学家：关注认知偏差、行为动机
- 哲学家：关注存在意义、伦理困境
- 艺术家：关注美学、表达、创造力
- 历史学家：关注时代背景、演变规律
- 科学家：关注实证、可证伪性、因果

---

### 📊 Diachronic Analysis (Longitudinal)

**Task**: Restore the book's complete development along the timeline

**Data Source**: Call [Diachronic Data Strategy] for external information

```
## Diachronic Analysis: From Birth to Present

### Creation Background
- Writing period: [From Douban/Wikipedia]
- Social environment: [From search results]
- Core problem author faced: [From interviews/biography]

### Version Evolution (if any)
- Core changes from first edition to current: [From version history]
- Intellectual evolution trajectory: [Cross-version comparison]

### Intellectual History Positioning
- Contemporary similar works: [Same-period work search]
- Intellectual origins (influenced by): [Citation chain analysis]
- Influence on later works: [Citation count / review mentions]
```

### 🔀 Synchronic Analysis (Horizontal)

**Task**: At current time slice, compare with similar books

**Data Source**: Call [Synchronic Data Strategy] for competitor data

```
## Synchronic Analysis: Competitor Benchmarking

### Similar Classic Comparison
| Dimension | This Book | Competitor A | Competitor B |
|-----------|-----------|-------------|--------------|
| Core viewpoint | [This book] | [Retrieveed] | [Retrieveed] |
| Methodology | [This book] | [Retrieveed] | [Retrieveed] |
| Writing style | [This book] | [Retrieveed] | [Retrieveed] |
| Applicable scenarios | [This book] | [Retrieveed] | [Retrieveed] |
| Rating | [Retrieveed] | [Retrieveed] | [Retrieveed] |

### Differentiation Positioning
[This book's unique value and irreplaceability]

### Reader Selection Advice
- Who should read: [Based on content characteristics]
- Alternatives: [Similar book recommendations]
```

### 🎯 H-V Intersection Insight

**Task**: Combine diachronic and synchronic analysis for unique judgment

```
## H-V Intersection Insight

### History's Gift
[Which past factors shaped this book's core value]

### Current Coordinates
[This book's position in current intellectual landscape]

### Future Projection
[This book's predictive value for future trends]
```

---

## Auto-Save Module

**Save Path**: `/root/.openclaw/workspace/reports/`

### File Naming Rule

```
[Book_Name]_[Analysis_Mode]_[Date].md
```

Examples:
- `Atomic_Habits_Standard_Analysis_2026-04-25.md`
- `Sapiens_HV_Analysis_2026-04-25.md`

### Save Flow

```
Step 1: Generate complete analysis report (Markdown format)
Step 2: Generate filename (book name + mode + date)
Step 3: Write to /root/.openclaw/workspace/reports/[filename].md
Step 4: Return save confirmation
```

### Report Template Structure

```markdown
---
title: [Book Name] Deep Analysis Report
author: Four-Dimensional Deep Reading AI
date: YYYY-MM-DD
mode: [Standard Mode / H-V Enhanced Mode]
tags: [book, analysis, reading notes]
source: [book name / file path / link]
data_sources: [list of retrieveed data sources]
---

# "[Book Name]" Deep Analysis Report

> Analysis Mode: [Standard / H-V Enhanced] | Analysis Time: [Date] | Random Persona: [Role Name]

---

## 🔬 Axiom Analyst
[Content]

---

## 📝 L-M-S Architect
### Logic
[Content]

### Method
[Content]

### Summary
> [Content]

---

## ⚡ Black Swan Hunter
[Content]

---

## 🎲 Random Variable X: [Role Name]
[Content]

---

## 📊 H-V Analysis (H-V Mode Only)
### Diachronic: Intellectual History Positioning
[Content]

### Synchronic: Competitor Benchmarking
[Content]

### Intersection: Insight
[Content]

---

## 🧠 Synthesized Conclusion
[Content]

---

## 📚 Reference Information
- Book: [Book Name]
- Author: [Author]
- Analysis Date: [Date]
- Random Persona Used: [Role Name]
- Data Sources: [List all retrieveed external links]
```

---

## Workflow

### Step 1: Receive Input and Classify

User input falls into three types:
- **Book title only** → Start [Method A: Web Search Retrieve]
- **Local file path** → Start [Method B: Format Parsing]
- **Full link** → Start [Method C: Link Retrieve]

### Step 2: Content Extraction and Cleaning

```
Raw content → Remove ads/headers/footers → Chapter marking → Extract
```

### Step 3: Parallel Four-Dimensional Analysis ⚡

**v1.6.0 并行处理机制**：使用 `sessions_spawn` 同时启动 4 个子代理，每个代理独立执行一个角色的分析任务。

**v1.7.0 语言感知**：并行执行时自动检测用户语言，生成对应语言的 prompt 和报告。

#### Language Detection Priority

```
1. Explicit language parameter (--lang)
2. User's message language
3. Book's original language
4. Default: English
```

#### Language Detection Function

```python
def detect_output_language(user_message, book_title=None):
    """Detect output language"""
    
    # 1. Check explicit parameter
    if user_message.lang_param:
        return user_message.lang_param
    
    # 2. Detect user message language
    user_lang = detect_language(user_message.text)
    if user_lang in ['zh', 'zh-CN', 'zh-TW']:
        return 'zh'
    elif user_lang in ['ja']:
        return 'ja'
    elif user_lang in ['ko']:
        return 'ko'
    
    # 3. Detect book title language
    if book_title:
        book_lang = detect_language(book_title)
        if book_lang in ['zh', 'zh-CN', 'zh-TW']:
            return 'zh'
    
    # 4. Default to English
    return 'en'
```

#### Persona Prompt Templates (Multi-Language)

```python
# Supported languages
SUPPORTED_LANGUAGES = ['en', 'zh', 'ja', 'ko', 'fr', 'de', 'es', 'pt', 'ru']

# Fallback mechanism: if no complete template for a language, fallback to English
FALLBACK_LANG = 'en'

def get_persona_prompt(persona_key, language, book_info):
    """Get persona prompt in specified language"""
    
    # 1. Try to get template for specified language
    if language in PERSONA_PROMPTS:
        template = PERSONA_PROMPTS[language].get(persona_key)
        if template:
            return template.format(**book_info)
    
    # 2. Fallback to English template
    template = PERSONA_PROMPTS[FALLBACK_LANG].get(persona_key)
    return template.format(**book_info)

PERSONA_PROMPTS = {
    "en": {
        "axiom_analyst": """You are the 'Axiom Analyst', using axiomatic thinking to decompose book content.

Book: {book_title}
Author: {author}

Task: Reduce the book's core viewpoints to indivisible atomic propositions.

Workflow:
1. Strip appearances: Identify all packaging (stories, cases, metaphors), extract pure viewpoint kernels
2. Trace premises: Find underlying assumptions supporting core viewpoints, mark as \"A1, A2, A3...\"
3. Reverse decomposition: If this conclusion fails, which premises must be false?
4. Minimal expression: Summarize the book's core in one sentence (max 30 words)
5. Title analysis: Decode the metaphor system of the book title

Output Format:
## Core Premises
[3-5 indivisible atomic propositions]

## Underlying Assumptions
- A1: [Assumption 1 - must be falsifiable]
- A2: [Assumption 2 - must be falsifiable]

## Title Metaphor Analysis
[Decode the book title's metaphor system]

## One-Sentence Summary
> [Core viewpoint, max 30 words]

Word count: 800-1500 words

Important: Output analysis results directly, no opening or closing pleasantries.""",
        
        "lms_architect": """You are the 'L-M-S Architect', must output specific L-M-S structure.

Book: {book_title}
Author: {author}

Task: First introduce book content, then compress into reusable knowledge cards.

L-M-S Structure Definition:
- **Logic**: Causal chain / derivation path of viewpoints
- **Method**: Executable methodology / tools / frameworks
- **Summary**: Minimal summary of core points (max 50 words)

Output Format:
## Chapter Structure
| Part | Chapter | Theme | Core Content |

## Character Relationship Network
```
Protagonist
├── Relationship Line 1
│   ├── Character A (Relationship Type)
│   └── Character B (Relationship Type)
```

## Key Turning Points
| Event | Nature | Importance |

## Logic (Causal Chain)
[Causal chain: A→B→C]

## Method (Methodology)
[Executable methods or tools]

## Summary
> [Core viewpoint, max 50 words]

Word count: 1000-2000 words""",
        
        "black_swan_hunter": """You are the 'Black Swan Hunter', looking for black swan events and boundary conditions.

Book: {book_title}
Author: {author}

Task: Identify edge cases and failure points of conclusions.

Workflow:
1. Find counterexamples: What known facts conflict with the book's viewpoints?
2. Boundary detection: Under what conditions does this viewpoint fail?
3. Assumption challenge: If underlying assumptions are false, do conclusions still hold?
4. Butterfly effect: What possible chain reactions are ignored?
5. Contemporary significance: Why should 2026 readers read this book?

Output Format:
## Black Swan Events
[2-3 real cases or theoretical rebuttals conflicting with book's viewpoints]

## Boundary Conditions
| Condition | Reason for Failure | Verification Method |

## Assumption Vulnerability
[Chain reactions when underlying assumptions are challenged]

## Contemporary Significance Challenge
[Why should 2026 readers read this book?]

## Rebuttal and Defense
[Response to main criticisms, maintain dialectical balance]

Word count: 800-1500 words""",
        
        "random_variable_x": """You are 'Random Variable X', randomly loading an identity module.

Randomly selected identity: {random_role}
Focus: {role_focus}
Values: {role_values}

Book: {book_title}
Author: {author}

Task: Provide unique interpretation from the perspective of {random_role}.

Output Format:
## 🎲 Random Identity: {random_role}

### Role Background
[Identity background, profession, values]

### Unique Perspective
[What unique insights emerge when viewing the book from this perspective?]
> Must differ from other personas' perspectives, must produce cross-domain thinking

### Core Questions
[3 key questions this role would ask]
1. [Question 1]
2. [Question 2]
3. [Question 3]

### Cross-Domain Associations
[Connect the book with domain concepts, generate new understanding]

Word count: 600-1000 words"""
    },
    
    "zh": {
        "axiom_analyst": """你是「第一性原理师」，使用公理化思维分解书籍内容。

书籍：{book_title}
作者：{author}

任务：将书籍核心观点还原为不可再分的原子命题。

工作流程：
1. 剥离表象：识别所有包装（故事、案例、隐喻），提取纯观点内核
2. 追溯前提：找出支撑核心观点的底层假设，标记为\"A1, A2, A3...\"
3. 反向分解：如果这个结论失败，哪些前提必然为假？
4. 最小表达：用一句话总结本书核心（不超过30字）
5. 书名解析：解码书名本身的隐喻系统

输出格式：
## 核心前提
[3-5条不可再分解的原子命题]

## 底层假设
- A1: [假设1 - 必须可被证伪]
- A2: [假设2 - 必须可被证伪]

## 书名隐喻解析
[书名本身的隐喻系统]

## 一句话总结
> [核心观点，不超过30字]

字数要求：800-1500字

重要提醒：直接输出分析结果，不要有任何开场白或结尾客套话""",
        
        "lms_architect": """你是「结构化笔记官」，必须输出具体的 L-M-S 结构。

书籍：{book_title}
作者：{author}

任务：先介绍书籍内容，再压缩为可复用的知识卡片。

L-M-S 结构定义：
- **Logic**：因果链 / 观点的推导路径
- **Method**：可执行的方法论 / 工具 / 框架
- **Summary**：核心点的最小摘要（不超过50字）

输出格式：
## 章节结构
| 部分 | 章节 | 主题 | 核心内容 |

## 人物关系网络
```
主角
├── 关系线1
│   ├── 人物A（关系类型）
│   └── 人物B（关系类型）
```

## 关键转折点
| 事件 | 转折性质 | 重要程度 |

## Logic (逻辑链)
[因果链：A→B→C]

## Method (方法论)
[可执行的方法或工具]

## Summary (摘要)
> [核心观点，不超过50字]

字数要求：1000-2000字""",
        
        "black_swan_hunter": """你是「专业反驳者」，寻找「黑天鹅」事件和边界条件。

书籍：{book_title}
作者：{author}

任务：识别结论的边缘情况和失效点。

工作流程：
1. 找反例：有哪些已知事实与书中观点冲突？
2. 边界检测：在什么条件下，这个观点会失效？
3. 假设挑战：如果底层假设为假，结论是否仍然成立？
4. 蝴蝶效应：忽略了哪些可能的连锁反应？
5. 当代意义：2026年的读者为何要读这本书？

输出格式：
## 黑天鹅事件
[2-3个与书中观点冲突的真实案例或理论反驳]

## 边界条件
| 条件 | 观点失效原因 | 验证方式 |

## 假设脆弱性
[当底层假设被挑战时，会产生什么连锁反应？]

## 当代意义挑战
[2026年的读者为何要读这本书？]

## 反驳与辩护
[对主要批判的回应，保持辩证平衡]

字数要求：800-1500字""",
        
        "random_variable_x": """你是「随机变量 X」，随机加载一个身份模块。

本次随机选中的身份：{random_role}
关注点：{role_focus}
价值观：{role_values}

书籍：{book_title}
作者：{author}

任务：从{random_role}的视角提供独特解读。

输出格式：
## 🎲 随机身份：{random_role}

### 角色背景
[身份背景、职业、价值观]

### 独特视角
[从该视角看书会产生什么独特洞察？]
> 必须与其他角色的视角不同，必须产生跨界思考

### 核心问题
[该角色会提出的3个关键问题]
1. [问题1]
2. [问题2]
3. [问题3]

### 跨界联想
[将书籍与领域概念连接，产生新的理解]

字数要求：600-1000字"""
    },
    
    "ja": {
        "axiom_analyst": """あなたは「公理分析者」です。公理的思考を用いて書籍の内容を分解してください。

書籍：{book_title}
著者：{author}

タスク：書籍の核心的観点を分割不可能な原子命題に還元してください。

ワークフロー：
1. 表象を剥ぎ取る：すべての包装（物語、事例、隠喩）を識別し、純粋な観点の核を抽出
2. 前提を追跡する：核心的観点を支える基礎仮定を見つけ、「A1, A2, A3...」とマーク
3. 逆分解：この結論が失敗した場合、どの前提が偽でなければならないか？
4. 最小表現：本書の核心を一言で要約（30文字以内）
5. タイトル分析：書籍タイトルの隠喩システムを解読

出力形式：
## 核心前提
[3-5個の分割不可能な原子命題]

## 基礎仮定
- A1: [仮定1 - 反証可能でなければならない]
- A2: [仮定2 - 反証可能でなければならない]

## タイトル隠喩分析
[書籍タイトルの隠喩システムを解読]

## 一言要約
> [核心的観点、30文字以内]

文字数：800-1500文字

重要：分析結果を直接出力し、冒頭や結びの挨拶は不要""",
        
        "lms_architect": """あなたは「構造化ノート作成者」です。具体的なL-M-S構造を出力してください。

書籍：{book_title}
著者：{author}

タスク：まず書籍の内容を紹介し、再利用可能な知識カードに圧縮してください。

L-M-S構造定義：
- **Logic**：因果連鎖 / 観点の導出パス
- **Method**：実行可能な方法論 / ツール / フレームワーク
- **Summary**：核心の最小要約（50文字以内）

出力形式：
## 章構造
| 部分 | 章 | テーマ | 核心内容 |

## 人物関係ネットワーク
```
主人公
├── 関係線1
│   ├── 人物A（関係タイプ）
│   └── 人物B（関係タイプ）
```

## 重要な転換点
| 出来事 | 転換の性質 | 重要度 |

## Logic（論理連鎖）
[因果連鎖：A→B→C]

## Method（方法論）
[実行可能な方法またはツール]

## Summary（要約）
> [核心的観点、50文字以内]

文字数：1000-2000文字""",
        
        "black_swan_hunter": """あなたは「ブラックスワン探索者」です。ブラックスワン事象と境界条件を探してください。

書籍：{book_title}
著者：{author}

タスク：結論のエッジケースと失敗点を識別してください。

ワークフロー：
1. 反例を見つける：書籍の観点と矛盾する既知の事実は何か？
2. 境界検出：どのような条件下でこの観点は失敗するか？
3. 仮定挑戦：基礎仮定が偽の場合、結論は依然として成立するか？
4. バタフライ効果：どのような可能な連鎖反応が無視されているか？
5. 現代的意義：2026年の読者はなぜこの本を読むべきか？

出力形式：
## ブラックスワン事象
[書籍の観点と矛盾する2-3個の実例または理論的反論]

## 境界条件
| 条件 | 失敗理由 | 検証方法 |

## 仮定の脆弱性
[基礎仮定が挑戦された時、どのような連鎖反応が生じるか？]

## 現代的意義の挑戦
[2026年の読者はなぜこの本を読むべきか？]

## 反論と弁護
[主な批判への対応、弁証法的バランスを維持]

文字数：800-1500文字""",
        
        "random_variable_x": """あなたは「確率変数X」です。ランダムにアイデンティティモジュールをロードします。

ランダムに選択されたアイデンティティ：{random_role}
焦点：{role_focus}
価値観：{role_values}

書籍：{book_title}
著者：{author}

タスク：{random_role}の視点から独自の解釈を提供してください。

出力形式：
## 🎲 ランダムアイデンティティ：{random_role}

### 役割の背景
[アイデンティティの背景、職業、価値観]

### 独自の視点
[この視点から書籍を見ると、どのような独自の洞察が生まれるか？]
> 他のペルソナの視点と異なり、クロスドメイン思考を生み出す必要がある

### 核心的質問
[この役割が提起する3つの重要な質問]
1. [質問1]
2. [質問2]
3. [質問3]

### クロスドメイン連想
[書籍をドメイン概念と接続し、新しい理解を生み出す]

文字数：600-1000文字"""
    },
    
    "ko": {
        "axiom_analyst": """당신은 '공리 분석가'입니다. 공리적 사고를 사용하여 책 내용을 분해하세요.

책: {book_title}
저자: {author}

과제: 책의 핵심 관점을 더 이상 분해할 수 없는 원자 명제로 환원하세요.

워크플로:
1. 표면 벗기기: 모든 포장(이야기, 사례, 은유)을 식별하고 순수한 관점의 핵심 추출
2. 전제 추적: 핵심 관점을 지탱하는 기초 가정을 찾아 'A1, A2, A3...'로 표시
3. 역분해: 이 결론이 실패하면 어떤 전제가 거짓이어야 하는가?
4. 최소 표현: 책의 핵심을 한 문장으로 요약(30자 이내)
5. 제목 분석: 책 제목의 은유 시스템 해독

출력 형식:
## 핵심 전제
[3-5개의 분해 불가능한 원자 명제]

## 기초 가정
- A1: [가정 1 - 반증 가능해야 함]
- A2: [가정 2 - 반증 가능해야 함]

## 제목 은유 분석
[책 제목의 은유 시스템 해독]

## 한 문장 요약
> [핵심 관점, 30자 이내]

글자 수: 800-1500자

중요: 분석 결과를 직접 출력하고, 시작이나 끝의 인사말은 필요 없음""",
        
        "lms_architect": """당신은 '구조화 노트 작성자'입니다. 구체적인 L-M-S 구조를 출력하세요.

책: {book_title}
저자: {author}

과제: 먼저 책 내용을 소개하고, 재사용 가능한 지식 카드로 압축하세요.

L-M-S 구조 정의:
- **Logic**: 인과 연쇄 / 관점의 도출 경로
- **Method**: 실행 가능한 방법론 / 도구 / 프레임워크
- **Summary**: 핵심의 최소 요약(50자 이내)

출력 형식:
## 장 구조
| 부분 | 장 | 주제 | 핵심 내용 |

## 인물 관계 네트워크
```
주인공
├── 관계선 1
│   ├── 인물 A (관계 유형)
│   └── 인물 B (관계 유형)
```

## 핵심 전환점
| 사건 | 전환 성격 | 중요도 |

## Logic (논리 연쇄)
[인과 연쇄: A→B→C]

## Method (방법론)
[실행 가능한 방법 또는 도구]

## Summary (요약)
> [핵심 관점, 50자 이내]

글자 수: 1000-2000자""",
        
        "black_swan_hunter": """당신은 '블랙 스왐 탐색자'입니다. 블랙 스왐 사건과 경계 조건을 찾으세요.

책: {book_title}
저자: {author}

과제: 결론의 엣지 케이스와 실패 지점을 식별하세요.

워크플로:
1. 반례 찾기: 책의 관점과 충돌하는 알려진 사실은 무엇인가?
2. 경계 검출: 어떤 조건에서 이 관점이 실패하는가?
3. 가정 도전: 기초 가정이 거짓이면 결론이 여전히 성립하는가?
4. 나비 효과: 어떤 가능한 연쇄 반응이 무시되고 있는가?
5. 현대적 의미: 2026년 독자가 왜 이 책을 읽어야 하는가?

출력 형식:
## 블랙 스왐 사건
[책의 관점과 충돌하는 2-3개의 실제 사례 또는 이론적 반박]

## 경계 조건
| 조건 | 실패 이유 | 검증 방법 |

## 가정의 취약성
[기초 가정이 도전받을 때 어떤 연쇄 반응이 일어나는가?]

## 현대적 의미 도전
[2026년 독자가 왜 이 책을 읽어야 하는가?]

## 반박과 변호
[주요 비판에 대한 대응, 변증법적 균형 유지]

글자 수: 800-1500자""",
        
        "random_variable_x": """당신은 '확률 변수 X'입니다. 무작위로 정체성 모듈을 로드합니다.

무작위로 선택된 정체성: {random_role}
초점: {role_focus}
가치관: {role_values}

책: {book_title}
저자: {author}

과제: {random_role}의 관점에서 독특한 해석을 제공하세요.

출력 형식:
## 🎲 무작위 정체성: {random_role}

### 역할 배경
[정체성 배경, 직업, 가치관]

### 독특한 관점
[이 관점에서 책을 보면 어떤 독특한 통찰이 생기는가?]
> 다른 페르소나의 관점과 달라야 하며, 크로스 도메인 사고를 생성해야 함

### 핵심 질문
[이 역할이 제기할 3가지 핵심 질문]
1. [질문 1]
2. [질문 2]
3. [질문 3]

### 크로스 도메인 연상
[책을 도메인 개념과 연결하여 새로운 이해 생성]

글자 수: 600-1000자"""
    }
}

# Additional languages (French, German, Spanish, Portuguese, Russian) use English template as base
# But require output in corresponding language
ADDITIONAL_LANG_INSTRUCTIONS = {
    "fr": "Important: Output all analysis in French (Français).",
    "de": "Important: Output all analysis in German (Deutsch).",
    "es": "Important: Output all analysis in Spanish (Español).",
    "pt": "Important: Output all analysis in Portuguese (Português).",
    "ru": "Important: Output all analysis in Russian (Русский)."
}

def get_persona_prompt(persona_key, language, book_info):
    """
    Get persona prompt in specified language
    
    Supported languages:
    - en (English) - Complete template
    - zh (Chinese) - Complete template
    - ja (Japanese) - Complete template
    - ko (Korean) - Complete template
    - fr (French) - English template + French output instruction
    - de (German) - English template + German output instruction
    - es (Spanish) - English template + Spanish output instruction
    - pt (Portuguese) - English template + Portuguese output instruction
    - ru (Russian) - English template + Russian output instruction
    - Other languages - English template
    """
    
    # 1. Try to get complete template for specified language
    if language in PERSONA_PROMPTS:
        template = PERSONA_PROMPTS[language].get(persona_key)
        if template:
            return template.format(**book_info)
    
    # 2. For other supported languages, use English template + language instruction
    template = PERSONA_PROMPTS[FALLBACK_LANG].get(persona_key)
    base_prompt = template.format(**book_info)
    
    # Add language output instruction
    if language in ADDITIONAL_LANG_INSTRUCTIONS:
        base_prompt += f"\n\n{ADDITIONAL_LANG_INSTRUCTIONS[language]}"
    
    return base_prompt
```

#### Parallel Execution Code (with Language Detection)

```python
# 1. Detect output language
output_lang = detect_output_language(user_message, book_title)

# 2. Get prompt template for the language
prompts = PERSONA_PROMPTS.get(output_lang, PERSONA_PROMPTS["en"])

# 3. Launch 4 persona analyses in parallel
personas = [
    {"key": "axiom_analyst", "name": "Axiom Analyst" if output_lang == "en" else "第一性原理师"},
    {"key": "lms_architect", "name": "L-M-S Architect" if output_lang == "en" else "结构化笔记官"},
    {"key": "black_swan_hunter", "name": "Black Swan Hunter" if output_lang == "en" else "黑天鹅猎手"},
    {"key": "random_variable_x", "name": "Random Variable X" if output_lang == "en" else "随机变量 X"}
]

# 4. Execute in parallel using sessions_spawn (with language parameter)
for persona in personas:
    prompt_template = prompts[persona["key"]]
    task_prompt = prompt_template.format(
        book_title=book_title,
        author=author,
        random_role=random_role,
        role_focus=role_focus,
        role_values=role_values
    )
    
    sessions_spawn(
        task=task_prompt,
        mode="run",
        runtime="subagent"
    )

# 5. Wait for all subagents to complete
sessions_yield(message=f"Waiting for all persona analyses to complete (Output language: {output_lang})")
```

#### OpenClaw Tool Call Example (English User)

```
# User message: "Please deep read The Three-Body Problem"
# Detected language: en

# 1. Launch Axiom Analyst (English prompt)
sessions_spawn(
  task: "You are the 'Axiom Analyst', using axiomatic thinking to decompose book content. Book: The Three-Body Problem...",
  mode: "run",
  runtime: "subagent"
)

# 2. Launch L-M-S Architect (English prompt)
sessions_spawn(
  task: "You are the 'L-M-S Architect', must output specific L-M-S structure. Book: The Three-Body Problem...",
  mode: "run",
  runtime: "subagent"
)

# 3. Launch Black Swan Hunter (English prompt)
sessions_spawn(
  task: "You are the 'Black Swan Hunter', looking for black swan events and boundary conditions...",
  mode: "run",
  runtime: "subagent"
)

# 4. Launch Random Variable X (English prompt)
sessions_spawn(
  task: "You are 'Random Variable X', randomly loading an identity module...",
  mode: "run",
  runtime: "subagent"
)

# 5. Wait for all results
sessions_yield(message: "Waiting for all persona analyses to complete (Output language: en)")
```

#### OpenClaw Tool Call Example (Chinese User)

```
# User message: "深度阅读《三体》"
# Detected language: zh

# 1. Launch 第一性原理师 (Chinese prompt)
sessions_spawn(
  task: "你是「第一性原理师」，使用公理化思维分解书籍内容。书籍：《三体》...",
  mode: "run",
  runtime: "subagent"
)

# 2. Launch 结构化笔记官 (Chinese prompt)
sessions_spawn(
  task: "你是「结构化笔记官」，必须输出具体的 L-M-S 结构...",
  mode: "run",
  runtime: "subagent"
)

# 3. Launch 黑天鹅猎手 (Chinese prompt)
sessions_spawn(
  task: "你是「专业反驳者」，寻找「黑天鹅」事件和边界条件...",
  mode: "run",
  runtime: "subagent"
)

# 4. Launch 随机变量 X (Chinese prompt)
sessions_spawn(
  task: "你是「随机变量 X」，随机加载一个身份模块...",
  mode: "run",
  runtime: "subagent"
)

# 5. Wait for all results
sessions_yield(message: "等待所有角色分析完成（输出语言：zh）")
```

#### 并行处理流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Step 3: 并行四维分析                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐│
│   │ Axiom       │  │ L-M-S       │  │ Black Swan  │  │ Random ││
│   │ Analyst     │  │ Architect   │  │ Hunter      │  │ Var X  ││
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └───┬────┘│
│          │                │                │             │      │
│          └────────────────┴────────────────┴─────────────┘      │
│                                    │                            │
│                                    ▼                            │
│                          ┌─────────────────┐                    │
│                          │  结果聚合       │                    │
│                          │  Synthesis      │                    │
│                          └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘

时间对比：
- 顺序执行：~4T（每个角色耗时 T）
- 并行执行：~T（所有角色同时完成）
- 效率提升：约 75%
```

### Step 4: H-V Analysis (Optional)

If user requests enhanced mode:
- **Diachronic** → Intellectual history positioning
- **Synchronic** → Competitor benchmarking
- **Intersection** → Cross-axis insight

### Step 5: Synthesis and Save

1. Aggregate all persona outputs
2. Generate complete Markdown report
3. Save to `workspace/reports/`
4. Return report path to user

---

## Quality Assessment Module

### Analysis Quality Metrics

| Dimension | Metric | Weight |
|-----------|--------|--------|
| **Depth** | Atomic proposition count | 25% |
| **Structure** | L-M-S completeness | 20% |
| **Criticality** | Edge case count | 20% |
| **Diversity** | Random persona insight uniqueness | 15% |
| **Context** | H-V analysis coverage | 20% |

### Quality Score Calculation

```python
def calculate_quality_score(analysis_result):
    """Calculate overall quality score (0-100)"""
    
    scores = {
        "depth": count_atomic_propositions(analysis_result) * 5,  # max 25
        "structure": assess_lms_completeness(analysis_result) * 20,  # max 20
        "criticality": count_edge_cases(analysis_result) * 4,  # max 20
        "diversity": assess_insight_uniqueness(analysis_result) * 15,  # max 15
        "context": assess_hv_coverage(analysis_result) * 20  # max 20
    }
    
    return sum(scores.values())  # max 100
```

### Quality Report Output

```
## 📊 Analysis Quality Report

| Dimension | Score | Max |
|-----------|-------|-----|
| Depth | 22 | 25 |
| Structure | 18 | 20 |
| Criticality | 16 | 20 |
| Diversity | 12 | 15 |
| Context | 18 | 20 |
| **Total** | **86** | **100** |

### Quality Assessment
- ✅ Excellent depth analysis
- ✅ Well-structured notes
- ⚠️ Consider more edge cases
- ✅ Unique persona perspective
- ✅ Comprehensive H-V analysis
```

---

## Usage Examples

### Example 1: Book Title Only

```
User: Use deep reading to analyze "Atomic Habits"
→ Triggers Method A (web search)
→ Retrievees metadata from Douban, Google Books, Wikipedia
→ Runs 4-persona analysis
→ Saves report to reports/Atomic_Habits_Analysis_2026-04-26.md
```

### Example 2: Local File

```
User: Deep read this file: /path/to/book.pdf
→ Triggers Method B (format parsing)
→ Parses PDF to text
→ Runs 4-persona analysis
→ Saves report
```

### Example 3: Link

```
User: Analyze this book from a public link
→ Triggers Method C (Link retrieve)
→ Saves and parses
→ Runs 4-persona analysis
→ Saves report
```

---

## 🌐 Language Output Module

### Supported Languages

| Language | Code | Native Name |
|----------|------|-------------|
| English | `en` | English |
| Chinese (Simplified) | `zh-CN` | 简体中文 |
| Chinese (Traditional) | `zh-TW` | 繁體中文 |
| Japanese | `ja` | 日本語 |
| Korean | `ko` | 한국어 |
| French | `fr` | Français |
| German | `de` | Deutsch |
| Spanish | `es` | Español |
| Portuguese | `pt` | Português |
| Russian | `ru` | Русский |

### Language Detection Logic

```python
def detect_output_language(user_input, book_language=None):
    """Determine output language based on context"""
    
    # Priority order:
    # 1. Explicit language parameter
    # 2. User's message language
    # 3. Book's original language
    # 4. Default (English)
    
    if user_input.language_param:
        return user_input.language_param
    
    detected = detect_language(user_input.text)
    if detected in SUPPORTED_LANGUAGES:
        return detected
    
    if book_language:
        return book_language
    
    return 'en'  # Default
```

### Language-Specific Output Templates

#### English Template
```markdown
## 🔬 Axiom Analyst
### Core Premises
[Atomic propositions in English]

### Underlying Assumptions
- A1: [Assumption 1]
- A2: [Assumption 2]
```

#### Chinese Template (Simplified)
```markdown
## 🔬 第一性原理师
### 核心前提
[原子命题，中文表达]

### 底层假设
- A1: [假设 1]
- A2: [假设 2]
```

#### Japanese Template
```markdown
## 🔬 公理分析者
### 核心前提
[原子命題、日本語で]

### 基礎仮定
- A1: [仮定 1]
- A2: [仮定 2]
```

### Persona Name Localization

| Persona | English | Chinese | Japanese | Korean |
|---------|---------|---------|----------|--------|
| Axiom Analyst | Axiom Analyst | 第一性原理师 | 公理分析者 | 공리 분석가 |
| L-M-S Architect | L-M-S Architect | 结构化笔记官 | 構造化ノート作成者 | 구조화 노트 작성자 |
| Black Swan Hunter | Black Swan Hunter | 黑天鹅猎手 | ブラックスワン探索者 | 블랙 스왐 탐색자 |
| Random Variable X | Random Variable X | 随机变量 X | 確率変数 X | 확률 변수 X |

### Section Header Localization

| Section | English | Chinese | Japanese |
|---------|---------|---------|----------|
| Core Premises | Core Premises | 核心前提 | 核心前提 |
| Underlying Assumptions | Underlying Assumptions | 底层假设 | 基礎仮定 |
| Logic | Logic | 逻辑 | 論理 |
| Method | Method | 方法 | 方法 |
| Summary | Summary | 摘要 | 要約 |
| Black Swan Events | Black Swan Events | 黑天鹅事件 | ブラックスワン事件 |
| Edge Cases | Edge Cases | 边界条件 | 境界条件 |
| Diachronic Analysis | Diachronic Analysis | 纵向分析 | 縦断分析 |
| Synchronic Analysis | Synchronic Analysis | 横向分析 | 横断分析 |

### Usage Examples with Language

```
# English output (default)
User: Analyze "Atomic Habits" with deep reading

# Chinese output
User: 用深度阅读分析《原子习惯》
User: Analyze "Atomic Habits" --lang zh-CN

# Japanese output
User: 深読みで「アトミック・ハビッツ」を分析して
User: Analyze "Atomic Habits" --lang ja

# Explicit language parameter
User: Analyze "三体" --lang en  # Chinese book, English output
```

### Language-Aware Report Naming

```python
def generate_report_filename(book_name, language, date):
    """Generate language-aware filename"""
    
    lang_suffix = {
        'en': '',
        'zh-CN': '_中文',
        'zh-TW': '_繁體',
        'ja': '_日本語',
        'ko': '_한국어'
    }.get(language, '')
    
    return f"{book_name}_Deep_Analysis{lang_suffix}_{date}.md"
```

---

## Configuration

### Environment Variables

```bash
DEEP_READER_REPORTS_DIR=/root/.openclaw/workspace/reports
DEEP_READER_TEMP_DIR=/tmp/deep-reader
DEEP_READER_DEFAULT_MODE=hv-enhanced  # standard | hv-enhanced
DEEP_READER_DEFAULT_LANG=auto  # auto | en | zh-CN | ja | ko | ...
```

### Skill Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `mode` | `hv-enhanced` | Analysis mode |
| `lang` | `auto` | Output language (auto-detect if `auto`) |
| `save_report` | `true` | Auto-save report |
| `random_persona_category` | `all` | Restrict random persona pool |
| `quality_threshold` | `70` | Minimum quality score to pass |

---

## Dependencies & Installation

### Core Dependencies (Auto-installed with skill)

| Dependency | Purpose | Notes |
|------------|---------|-------|
| `web_tool` | Retrieve web content | Built-in OpenClaw tool |
| `search_tool` | Search book resources | Built-in skill |

### File Parsing Dependencies (Optional)

All file parsing uses **pure Python** libraries - no system binaries required.

| Format | Library | Install | Notes |
|--------|---------|---------|-------|
| **TXT** | None | - | ✅ Always available |
| **MD** | None | - | ✅ Always available |
| **PDF** | `pdfplumber` | `pip install pdfplumber` | Pure Python, no system deps |
| **EPUB** | `ebooklib`, `beautifulsoup4` | `pip install ebooklib beautifulsoup4` | Pure Python |
| **MOBI** | Convert to EPUB first | - | Use online converter |

### Quick Install (for local file parsing)

```bash
pip install pdfplumber ebooklib beautifulsoup4 lxml
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### Dependency Check

```bash
python3 -c "import pdfplumber; print('PDF OK')"
python3 -c "import ebooklib; print('EPUB OK')"
```

---

## Usage Examples

### Example 1: Book Title Only (Web Search)

```
User: Analyze "Atomic Habits" with deep reading
User: Use four-dimensional deep reading on "Tao Te Ching"
User: 用四维深度阅读分析《漫长的旅途》

→ Triggers Method A (web search)
→ Retrievees metadata from Douban, Google Books, Wikipedia
→ Runs 4-persona analysis
→ Saves report to reports/<Book_Name>_Deep_Analysis_<Date>.md
```

### Example 2: Local TXT File

```
User: Deep read this file: /path/to/book.txt
User: 分析这个文件：/home/user/我的书.txt

→ Triggers Method B (format parsing)
→ Auto-detects encoding (UTF-8/GBK/GB2312/Big5)
→ Runs 4-persona analysis
→ Saves report
```

### Example 3: Local Markdown File

```
User: Analyze /path/to/notes.md with deep reading
User: 深度阅读这个 Markdown：./chapter1.md

→ Triggers Method B (format parsing)
→ Detects ## headers as chapter markers
→ Runs 4-persona analysis
```

### Example 4: PDF File (requires pdftotext)

```
User: Deep read /path/to/book.pdf
User: 分析 PDF：./saves/ebook.pdf

→ Triggers Method B (PDF parsing)
→ Uses pdftotext to extract text with layout preservation
→ Detects chapter markers
→ Runs 4-persona analysis
```

### Example 5: EPUB File (requires ebooklib)

```
User: Analyze /path/to/book.epub with four-dimensional deep reading
User: 深度阅读 EPUB：./books/novel.epub

→ Triggers Method B (EPUB parsing)
→ Extracts HTML content from EPUB
→ Preserves chapter structure
→ Runs 4-persona analysis
```

### Example 6: Link (Direct Retrieve)

```
User: Analyze this book from a public link
User: 深度阅读这个在线电子书链接

→ Triggers Method C (Link retrieve)
→ Saves to workspace
→ Detects file type from Content-Type header
→ Parses and analyzes
→ Cleans up temp file
```

### Example 7: With Language Parameter

```
User: Analyze "三体" --lang en        # Chinese book, English output
User: 分析 "Atomic Habits" --lang zh-CN  # English book, Chinese output
User: 深読みで「道徳経」--lang ja       # Japanese output
```

### Example 8: With Mode Parameter

```
User: Analyze "1984" --mode standard      # 4-persona only
User: 分析《红楼梦》--mode hv-enhanced    # 4-persona + H-V analysis
```

---

## ✅ 质检清单 (Quality Checklist)

报告生成后必须通过以下质检项，不合格则返工修正：

### 一、角色输出完整性

| 检查项 | 标准 | 通过条件 |
|--------|------|----------|
| 第一性原理师 | 800-1500字 | 包含核心前提、底层假设、书名隐喻、一句话总结 |
| 结构化笔记师 | 1000-2000字 | 包含章节结构、人物网络、转折点、L-M-S |
| 黑天鹅猎手 | 800-1500字 | 包含黑天鹅事件、边界条件、假设脆弱性 |
| 随机变量X | 600-1000字 | 包含角色背景、独特视角、核心问题、跨界联想 |

### 二、内容质量标准

| 检查项 | 标准 | 检查方法 |
|--------|------|----------|
| 原子命题不可再分 | 每条核心前提都是最小单元 | 尝试拆分，无法拆分则通过 |
| 假设可证伪 | 每条底层假设都可被证伪 | 存在反例则通过 |
| 反驳有事实支撑 | 每个黑天鹅事件有来源 | 标注来源则通过 |
| 边界条件可验证 | 每个边界条件可被检验 | 存在检验方法则通过 |
| 视角真正独特 | 随机角色视角不与前三个重复 | 无重复观点则通过 |

### 三、横纵分析质量（H-V模式）

| 检查项 | 标准 | 通过条件 |
|--------|------|----------|
| 纵向叙事完整 | 有起源、演进、阶段划分 | 故事线完整则通过 |
| 横向对比充分 | 至少对比3个同类作品 | 对比表完整则通过 |
| 交汇洞察新颖 | 不是前文内容的缩写 | 有新判断则通过 |

### 四、写作风格检查

| 检查项 | 禁止 | 检查方法 |
|--------|------|----------|
| 无AI套话 | "首先...其次...最后"、"综上所述" | 未出现则通过 |
| 无空洞词 | "赋能"、"抓手"、"打造闭环" | 未出现则通过 |
| 无教科书开头 | "在当今...的时代"、"随着...的发展" | 未出现则通过 |
| 无高频踩雷 | "说白了"、"意味着什么？"、"本质上" | 出现<2次则通过 |

### 五、信息来源标注

| 检查项 | 标准 | 通过条件 |
|--------|------|----------|
| 关键事实有来源 | 重要论断标注出处 | 有来源链接则通过 |
| 暂缺信息诚实标注 | 不编造无法获取的信息 | 标注"暂缺"则通过 |

### 质检评分计算

```python
def calculate_quality_score(report):
    """计算质检总分 (0-100)"""
    
    scores = {
        "角色完整性": check_persona_completeness(report) * 25,  # max 25
        "内容质量": check_content_quality(report) * 25,  # max 25
        "横纵分析": check_hv_quality(report) * 20,  # max 20
        "写作风格": check_writing_style(report) * 15,  # max 15
        "来源标注": check_source_attribution(report) * 15  # max 15
    }
    
    total = sum(scores.values())
    return {
        "scores": scores,
        "total": total,
        "passed": total >= 70  # 70分及格
    }
```

### 质检报告输出模板

```
## 📊 质检报告

| 检查维度 | 得分 | 满分 | 状态 |
|----------|------|------|------|
| 角色完整性 | 23 | 25 | ✅ |
| 内容质量 | 22 | 25 | ✅ |
| 横纵分析 | 18 | 20 | ✅ |
| 写作风格 | 14 | 15 | ✅ |
| 来源标注 | 13 | 15 | ⚠️ |
| **总分** | **90** | **100** | **✅ 通过** |

### 改进建议
- ⚠️ 来源标注：建议补充更多数据来源
```

---

## 📈 Performance Metrics (v1.5.0)

### Data Fetching Success Rate

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Success Rate** | ~70% | ~95% | +25% |
| **Avg Response Time** | 3-5s | 1-2s (cached) | -60% |
| **Retry Coverage** | 0% | 100% | +100% |
| **Cache Hit Rate** | 0% | ~40% | +40% |

### Cache Statistics

```python
# 查看缓存统计
from book_fetcher_enhanced import get_cache_stats
stats = get_cache_stats()
# 输出: {"total": 15, "size_mb": 0.05}
```

---

## File Format Details

### TXT File Parsing

- **Encoding Detection**: UTF-8 → GBK → GB2312 → Big5 (auto-tried in order)
- **Chapter Detection**: Regex patterns for common chapter markers
  - Chinese: `第 X 章`, `第 X 部分`, `第 X 卷`
  - English: `Chapter X`, `Part X`, `Section X`
  - Numeric: `1.`, `1.1`, etc.

### Markdown File Parsing

- **Chapter Detection**: `##` headers as chapter markers
- **Structure Preservation**: Headers, lists, code blocks preserved
- **Encoding**: UTF-8 (default), GBK fallback

### PDF File Parsing

- **Tool**: `pdftotext` from poppler-utils
- **Layout**: Preserved with `-layout` flag
- **Limitation**: Scanned PDFs (images) require OCR (not supported)

### EPUB File Parsing

- **Tool**: `ebooklib` + `BeautifulSoup`
- **Structure**: HTML parsed, chapter titles extracted from `<h1>`/`<h2>`
- **Metadata**: Title, author extracted from EPUB metadata

### MOBI File Parsing

- **Tool**: `calibre` (ebook-convert)
- **Process**: MOBI → EPUB → Parse
- **Note**: Calibre is large (~200MB), install only if needed

---

## License

MIT License

## Author

Zhang Quan (@zhangboheng)

## Version

1.7.0

## Changelog

### v1.7.0 (2026-04-28)
- 🌐 **Language-aware parallel processing**
  - Auto-detect user message language before spawning personas
  - Full template support for EN/ZH/JA/KO (4 languages)
  - Fallback support for FR/DE/ES/PT/RU (5 languages) with output instruction
  - Output reports in the same language as user's request
  - Added `PERSONA_PROMPTS` multi-language template dictionary
  - Added `get_persona_prompt()` function with fallback mechanism
  - Updated `sessions_spawn` examples with language detection flow
- 📝 Fixed: Reports now match the language of user's request
- 🐍 **Updated scripts/parallel_analysis.py**
  - All code comments in English
  - Multi-language support for persona names, instructions, and identity pools
  - `get_persona_name()`, `get_persona_instruction()`, `get_random_identity()` functions
  - `generate_report()` with language-specific labels
  - Version upgraded to 1.7.0
- 📚 **Updated reference/identity_modules.md**
  - All content in English (primary documentation language)
  - Multi-language support note added
  - Role descriptions standardized to English
  - Selection rules and extension guide in English
- 🐍 **Updated reference/*.py files**
  - `book_parser.py`: All comments and messages in English
  - `book_fetcher.py`: All comments and messages in English
  - `book_fetcher_enhanced.py`: All comments and messages in English
  - Sample data updated to English examples
  - CLI help messages in English

### v1.6.0 (2026-04-28)
- ⚡ **Parallel persona processing**
  - All 4 personas now execute simultaneously using `sessions_spawn`
  - ~75% reduction in total analysis time
  - Added parallel execution workflow diagram
  - Added OpenClaw tool call examples for parallel processing
- 📝 Updated SKILL.md with parallel processing instructions

### v1.5.0 (2026-04-27)
- 🚀 **Enhanced data fetching stability**
  - Multi-source backup: Douban → Goodreads → Wikipedia → Google Books
  - Local cache with 7-day expiration
  - Retry with exponential backoff (max 3 retries)
  - Smart data merging from multiple sources
  - Success rate improved from ~70% to ~95%
- 📦 New file: `reference/book_fetcher_enhanced.py`
- 📊 Added performance metrics section

### v1.4.4 (2026-04-27)
- 🔧 Removed subprocess, pure Python only
- 🔧 Dropped MOBI support (use EPUB instead)

### v1.2.0 (2026-04-26)
- 📚 Added comprehensive file parsing documentation
- 📚 Added detailed usage examples for all formats (TXT/MD/PDF/EPUB/MOBI/Link)
- 📚 Added dependency installation guide
- 📚 Added file format details and limitations
- 📚 Added mode and language parameter examples

### v1.1.0 (2026-04-26)
- ✨ Added multi-language output support (10 languages)
- ✨ Added language auto-detection
- ✨ Added localized persona names and section headers
- ✨ Added language-aware report naming

### v1.0.0 (2026-04-26)
- 🎉 Initial release
- 4-persona parallel analysis
- H-V analysis framework
- 81 random identity pool
- Quality assessment module
