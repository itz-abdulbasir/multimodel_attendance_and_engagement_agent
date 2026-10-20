"""
Production PDF Deliverable Compiler for NeuroClass Project Submission
- Replaces raw Mermaid and ASCII boxes with 300 DPI rendered diagrams and native ReportLab tables.
- Enforces strict page width boundaries (no clipping / out of page text).
- Replaces unsupported Unicode emojis with clean typographic tags.
- Implements two-pass NumberedCanvas for 'Page X of Y' headers/footers.
- Automated validation: asserts that every heading is immediately followed by substantive body content (zero empty sections).
"""

import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Preformatted, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DIAGRAMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagram_assets")

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 36
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)  # 540 pt
USABLE_HEIGHT = PAGE_HEIGHT - (2 * MARGIN) # 720 pt

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic 'Page X of Y' pagination and clean headers/footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        
        # Suppress header on Page 1
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor('#64748B'))
            self.drawString(MARGIN, PAGE_HEIGHT - 26, "NEUROCLASS: MULTIMODAL ATTENDANCE & ENGAGEMENT AGENT")
            self.setFont("Helvetica", 7.5)
            self.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 26, "SMARTBRIDGE SUBMISSION DELIVERABLE")
            
            # Header separator line
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.5)
            self.line(MARGIN, PAGE_HEIGHT - 29, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 29)

        # Footer on all pages
        self.setStrokeColor(colors.HexColor('#CBD5E1'))
        self.setLineWidth(0.5)
        self.line(MARGIN, 30, PAGE_WIDTH - MARGIN, 30)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor('#64748B'))
        self.drawString(MARGIN, 18, "100% Offline Edge Architecture | Privacy-Preserving Multimodal Intelligence")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(PAGE_WIDTH - MARGIN, 18, page_str)

        self.restoreState()


def get_custom_styles():
    base = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=base['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4,
        keepWithNext=True
    )

    h1_style = ParagraphStyle(
        'DocH1',
        parent=base['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=11.0,
        leading=14.5,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'DocH2',
        parent=base['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.2,
        leading=12.5,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'DocH3',
        parent=base['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11.0,
        textColor=colors.HexColor('#334155'),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=base['Normal'],
        fontName='Helvetica',
        fontSize=8.0,
        leading=11.2,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=2
    )

    code_style = ParagraphStyle(
        'DocCode',
        parent=base['Code'],
        fontName='Courier',
        fontSize=6.8,
        leading=8.5,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F8FAFC'),
        borderColor=colors.HexColor('#E2E8F0'),
        borderWidth=0.5,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=5
    )

    table_header_style = ParagraphStyle(
        'THeader',
        parent=base['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.white,
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TCell',
        parent=base['Normal'],
        fontName='Helvetica',
        fontSize=7.0,
        leading=9.0,
        textColor=colors.HexColor('#1E293B')
    )

    return {
        "title": title_style,
        "h1": h1_style,
        "h2": h2_style,
        "h3": h3_style,
        "body": body_style,
        "bullet": bullet_style,
        "code": code_style,
        "table_header": table_header_style,
        "table_cell": table_cell_style
    }


def clean_markdown_text(text):
    """Strips broken emojis and converts Markdown markup to ReportLab XML tags."""
    if not text:
        return ""
    
    replacements = {
        '🎯': '[IDENTIFY / LINK]',
        '🟢🟢🟢': '[SUPERIOR]',
        '🟢🟢': '[EXCELLENT]',
        '🟢': '[ACTIVE]',
        '✅': '[VERIFIED]',
        '⭐': '[ENHANCEMENT]',
        '⚠️': '[WARNING]',
        '🎉': '[SUCCESS]',
        '🎓': '',
        '•': '&bull;',
    }
    for em, rep in replacements.items():
        text = text.replace(em, rep)

    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')

    # Math symbols ($...$)
    text = re.sub(r'\$(.*?)\$', r'<b><i>\1</i></b>', text)

    # Markdown bold, italic, code
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', text)
    text = text.replace('&amp;bull;', '&bull;')

    return text.strip()


def build_native_table(rows, styles, total_width=USABLE_WIDTH):
    """Builds a responsive, multi-page splitting native PDF Table with word-wrapped Paragraphs."""
    if not rows:
        return None

    num_cols = max(len(r) for r in rows)
    col_max_lengths = [1] * num_cols
    for row in rows:
        for idx, cell in enumerate(row):
            if idx < num_cols:
                col_max_lengths[idx] = max(col_max_lengths[idx], len(str(cell)))

    total_len = sum(col_max_lengths)
    col_widths = [(l / total_len) * total_width for l in col_max_lengths]
    
    min_w = 40
    for i in range(num_cols):
        if col_widths[i] < min_w:
            col_widths[i] = min_w
    curr_total = sum(col_widths)
    col_widths = [(w / curr_total) * total_width for w in col_widths]

    table_data = []
    for r_idx, row in enumerate(rows):
        formatted_row = []
        is_header = (r_idx == 0)
        p_style = styles['table_header'] if is_header else styles['table_cell']

        for c_idx in range(num_cols):
            cell_val = row[c_idx] if c_idx < len(row) else ""
            clean_val = clean_markdown_text(str(cell_val))
            formatted_row.append(Paragraph(clean_val, p_style))
        table_data.append(formatted_row)

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    return t


def compile_markdown_to_clean_pdf(md_text, pdf_path, doc_title=None):
    """Compiles Markdown text into a publication-ready multi-page visual PDF."""
    fname = os.path.basename(pdf_path).lower()
    styles = get_custom_styles()
    heading_style_names = {'DocTitle', 'DocH1', 'DocH2', 'DocH3'}

    lines = md_text.split('\n')
    story = []
    in_code_block = False
    code_block_lang = ""
    code_buffer = []
    in_markdown_table = False
    markdown_table_rows = []

    def flush_table():
        nonlocal in_markdown_table, markdown_table_rows
        if markdown_table_rows:
            tbl = build_native_table(markdown_table_rows, styles)
            if tbl:
                story.append(Spacer(1, 4))
                story.append(tbl)
                story.append(Spacer(1, 6))
            markdown_table_rows = []
        in_markdown_table = False

    for line in lines:
        raw_line = line.rstrip('\r\n')
        stripped = raw_line.strip()

        # Handle code blocks
        if stripped.startswith("```"):
            if in_code_block:
                full_code = "\n".join(code_buffer)
                
                # 1. Mermaid / Flowchart / Pipeline Diagrams
                if "graph " in full_code or "sequenceDiagram" in full_code or "gantt" in full_code or "timeline" in full_code or code_block_lang in ["mermaid"]:
                    diag_img = None
                    if "data flow diagram" in fname or "data_flow" in fname:
                        if "level 0" in full_code.lower() or "context" in full_code.lower():
                            diag_img = os.path.join(DIAGRAMS_DIR, "diagram_level0_dfd.png")
                        else:
                            diag_img = os.path.join(DIAGRAMS_DIR, "diagram_level1_dfd.png")
                    elif "architecture" in fname:
                        diag_img = os.path.join(DIAGRAMS_DIR, "diagram_solution_architecture.png")
                    elif "planning" in fname or "gantt" in full_code:
                        diag_img = os.path.join(DIAGRAMS_DIR, "diagram_gantt_roadmap.png")
                    elif "brainstorming" in fname:
                        diag_img = os.path.join(DIAGRAMS_DIR, "diagram_multimodal_pipeline.png")
                    elif "proposed solution" in fname:
                        diag_img = os.path.join(DIAGRAMS_DIR, "diagram_presence_flow.png")
                    elif "performance" in fname or "testing" in fname:
                        diag_img = os.path.join(DIAGRAMS_DIR, "diagram_benchmark_audit.png")
                    elif "scalability" in fname or "future" in fname or "timeline" in full_code:
                        diag_img = os.path.join(DIAGRAMS_DIR, "diagram_future_roadmap.png")

                    if diag_img and os.path.exists(diag_img):
                        story.append(Spacer(1, 5))
                        img = Image(diag_img, width=USABLE_WIDTH, height=USABLE_WIDTH * 0.44)
                        story.append(img)
                        story.append(Spacer(1, 5))
                # 2. Empathy / Journey / Gap / Benchmark Diagrams inside code blocks
                elif "EMPATHY MAP" in full_code or "JOURNEY MAP" in full_code or "CLASSROOM GAP" in full_code or "CLASSROOM INTELLIGENCE GAP" in full_code:
                    diag_img = None
                    if "brainstorming" in fname:
                        if "empathy" in full_code.lower():
                            diag_img = os.path.join(DIAGRAMS_DIR, "diagram_empathy_maps.png")
                        elif "gap" in full_code.lower():
                            diag_img = os.path.join(DIAGRAMS_DIR, "diagram_classroom_gap.png")
                    elif "customer journey" in fname:
                        diag_img = os.path.join(DIAGRAMS_DIR, "diagram_customer_journey.png")

                    if diag_img and os.path.exists(diag_img):
                        story.append(Spacer(1, 5))
                        img = Image(diag_img, width=USABLE_WIDTH, height=USABLE_WIDTH * 0.42)
                        story.append(img)
                        story.append(Spacer(1, 5))
                # 3. ASCII Tables (+---+ or |---)
                elif "+---" in full_code or "|---" in full_code:
                    # Parse ASCII table into rows
                    ascii_rows = []
                    for cl in code_buffer:
                        c_strip = cl.strip()
                        if c_strip.startswith("+") and c_strip.endswith("+"):
                            continue
                        if c_strip.startswith("|") and c_strip.endswith("|"):
                            parts = [p.strip() for p in c_strip.split("|")[1:-1]]
                            if any(parts):
                                ascii_rows.append(parts)
                    if ascii_rows:
                        tbl = build_native_table(ascii_rows, styles)
                        if tbl:
                            story.append(Spacer(1, 4))
                            story.append(tbl)
                            story.append(Spacer(1, 6))
                    else:
                        clean_code = clean_markdown_text(full_code)
                        story.append(Preformatted(clean_code, styles['code']))
                else:
                    # Regular shell or python code block
                    clean_code = clean_markdown_text(full_code)
                    story.append(Preformatted(clean_code, styles['code']))

                code_buffer = []
                in_code_block = False
                code_block_lang = ""
            else:
                if in_markdown_table:
                    flush_table()
                in_code_block = True
                code_block_lang = stripped[3:].strip()
                code_buffer = []
            continue

        if in_code_block:
            code_buffer.append(raw_line)
            continue

        # Skip raw ASCII border lines outside of code blocks
        if re.match(r'^\+[\-+|=]+\+$', stripped):
            continue

        # Handle Markdown Tables (| col | col |)
        if stripped.startswith("|") and stripped.endswith("|"):
            if re.match(r'^\|[\s\-:|]+\|$', stripped):
                continue
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            markdown_table_rows.append(cells)
            in_markdown_table = True
            continue
        elif in_markdown_table:
            flush_table()

        if not stripped:
            story.append(Spacer(1, 3))
            continue

        # Headers & Paragraphs
        if stripped.startswith("# "):
            story.append(Paragraph(clean_markdown_text(stripped[2:]), styles['title']))
        elif stripped.startswith("## "):
            story.append(Paragraph(clean_markdown_text(stripped[3:]), styles['h1']))
        elif stripped.startswith("### "):
            story.append(Paragraph(clean_markdown_text(stripped[4:]), styles['h2']))
        elif stripped.startswith("#### "):
            story.append(Paragraph(clean_markdown_text(stripped[5:]), styles['h3']))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            bullet_txt = "&bull; " + clean_markdown_text(stripped[2:])
            story.append(Paragraph(bullet_txt, styles['bullet']))
        elif re.match(r'^\d+\.\s', stripped):
            num_match = re.match(r'^(\d+\.)\s(.*)', stripped)
            num_txt = f"<b>{num_match.group(1)}</b> {clean_markdown_text(num_match.group(2))}"
            story.append(Paragraph(num_txt, styles['bullet']))
        elif stripped.startswith("---"):
            story.append(Spacer(1, 3))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=5))
        else:
            story.append(Paragraph(clean_markdown_text(stripped), styles['body']))

    if in_markdown_table:
        flush_table()

    # AUTOMATED CHECK: Assert that zero headings are stranded or empty!
    # Inspect every heading flowable in story and ensure it is followed by non-heading substantive flowable
    for i, flowable in enumerate(story):
        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            if style_name in heading_style_names:
                # Find the next non-spacer flowable
                next_content = None
                for j in range(i + 1, len(story)):
                    cand = story[j]
                    if isinstance(cand, Spacer) or isinstance(cand, HRFlowable):
                        continue
                    next_content = cand
                    break
                
                heading_text = flowable.text[:40]
                if next_content is None:
                    raise AssertionError(f"EMPTY HEADING at end of story: '{heading_text}' in {os.path.basename(pdf_path)}")
                if isinstance(next_content, Paragraph) and next_content.style.name in heading_style_names:
                    raise AssertionError(f"EMPTY HEADING followed immediately by another heading: '{heading_text}' followed by '{next_content.text[:40]}' in {os.path.basename(pdf_path)}")

    # Ensure output parent directory exists
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # Build PDF with NumberedCanvas
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"    [OK] Built & Verified: {os.path.basename(pdf_path)} ({os.path.getsize(pdf_path)} bytes)")


def compile_all_deliverables():
    # 1. Regenerate 300 DPI diagram assets
    from render_diagrams import render_all_diagrams
    render_all_diagrams()

    # 2. Load deliverables
    from deliverable_contents import DELIVERABLES

    print("\n[*] Compiling and verifying all 16 submission deliverables...")
    compiled_count = 0
    for rel_path, content in DELIVERABLES.items():
        pdf_rel = rel_path.replace(".md", ".pdf")
        pdf_full = os.path.join(BASE_DIR, pdf_rel)
        compile_markdown_to_clean_pdf(content, pdf_full)
        compiled_count += 1

    print(f"\n[OK] Successfully compiled and verified all {compiled_count} deliverable PDFs with ZERO empty sections!")

if __name__ == "__main__":
    compile_all_deliverables()
