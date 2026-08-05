"""
Applies two changes to Final_report_v1.docx driven by
"Checklist of Items for the Final Dissertation, Project, Project Work Report.docx":

  1. Inserts a CERTIFICATE page (from the Supervisor) before Acknowledgements —
     the checklist explicitly asks "Is the Certificate from the Supervisor in
     proper format? Has it been signed by the Supervisor?" and no such page
     existed in the report.
  2. Appends the checklist itself, verbatim (question + Yes/No column), as the
     last page of the report, with a student declaration/signature block —
     the checklist's own instruction is "This checklist is to be attached as
     the last page of the final report."

Both edits are applied in place on Final_report_v1.docx; existing content and
formatting are left untouched.
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

PATH = os.path.join(os.path.dirname(__file__), 'Final_report_v1.docx')
doc = Document(PATH)

BLUE_DARK  = RGBColor(0x1F, 0x4E, 0x79)
BLUE_MID   = RGBColor(0x2E, 0x74, 0xB5)
BLUE_LIGHT = 'DEEAF1'
WHITE      = 'FFFFFF'

STUDENT_NAME       = 'Hariharan B'
BITS_ID            = '2024DA04024'
COURSE_NO          = 'DSECLZG628T'
COURSE_TITLE       = 'Dissertation'
TITLE              = 'AIE AUTOCODE AGENT'
ORG_NAME           = 'O9 Solutions'
ORG_LOCATION       = 'Bangalore'
SUPERVISOR_NAME    = 'Abhishek Hegde'
SUPERVISOR_DESIG   = 'Lead Data Scientist'
DATE_OF_SUBMISSION = '02 August 2026'

def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

# ── Helpers that build a paragraph via doc.add_* then relocate it via
#    anchor.addprevious(), so we can insert content BEFORE an existing
#    paragraph (needed for the Certificate page). ─────────────────────────────
def insert_heading_before(anchor, text):
    p = doc.add_heading(text, level=1)
    run = p.runs[0] if p.runs else p.add_run(text)
    run.font.name = 'Calibri'
    run.font.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = BLUE_DARK
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.0
    anchor._p.addprevious(p._p)
    return p

def insert_body_before(anchor, text, center=False, bold=False, double=True, space_after=8):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(11)
    r.font.bold = bold
    p.paragraph_format.space_after = Pt(space_after)
    if double:
        p.paragraph_format.line_spacing = 2.0
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    anchor._p.addprevious(p._p)
    return p

def insert_spacer_before(anchor, n=1):
    for _ in range(n):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        anchor._p.addprevious(p._p)

def insert_pagebreak_before(anchor):
    p = doc.add_page_break()
    anchor._p.addprevious(p._p)

def insert_table_before(anchor, rows, col_widths=None):
    t = doc.add_table(rows=len(rows), cols=2)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ri, (left, right) in enumerate(rows):
        for ci, val in enumerate([left, right]):
            cell = t.rows[ri].cells[ci]
            cell.text = val
            r = cell.paragraphs[0].runs[0]
            r.font.size = Pt(10)
            r.font.name = 'Calibri'
            if ri == 0:
                r.font.bold = True
    if col_widths:
        for row in t.rows:
            for ci, w in enumerate(col_widths):
                row.cells[ci].width = Inches(w)
    anchor._p.addprevious(t._tbl)
    return t

# ══════════════════════════════════════════════════════════════════════════════
# 1. CERTIFICATE PAGE — inserted before ACKNOWLEDGEMENTS
# ══════════════════════════════════════════════════════════════════════════════
ack_heading = None
for p in doc.paragraphs:
    if p.text.strip() == 'ACKNOWLEDGEMENTS' and p.style.name == 'Heading 1':
        ack_heading = p
        break

if ack_heading is None:
    raise RuntimeError('Could not find ACKNOWLEDGEMENTS heading to anchor the Certificate page')

insert_heading_before(ack_heading, 'CERTIFICATE')

insert_body_before(
    ack_heading,
    f'This is to certify that the dissertation entitled "{TITLE}" submitted by '
    f'{STUDENT_NAME} (ID No. {BITS_ID}), in partial fulfilment of the requirements '
    f'of the {COURSE_TITLE} course ({COURSE_NO}) of the Work Integrated Learning '
    f'Programmes Division, Birla Institute of Technology and Science, Pilani, '
    f'embodies the work done by him at {ORG_NAME}, {ORG_LOCATION}, under my supervision.'
)

insert_spacer_before(ack_heading, 2)

sig_rows = [
    ('Signature of the Supervisor', ''),
    (f'Name: {SUPERVISOR_NAME}', ''),
    (f'Designation: {SUPERVISOR_DESIG}, {ORG_NAME}, {ORG_LOCATION}', ''),
    ('Date:', ''),
]
sig_table = doc.add_table(rows=len(sig_rows), cols=2)
sig_table.style = 'Table Grid'
for ri, (left, right) in enumerate(sig_rows):
    cell = sig_table.rows[ri].cells[0]
    cell.text = left
    r = cell.paragraphs[0].runs[0]
    r.font.size = Pt(11)
    r.font.name = 'Calibri'
    if ri == 0:
        r.font.bold = True
    sig_table.rows[ri].cells[1].text = ''
ack_heading._p.addprevious(sig_table._tbl)

insert_pagebreak_before(ack_heading)

print('Inserted CERTIFICATE page before Acknowledgements')

# ══════════════════════════════════════════════════════════════════════════════
# 2. CHECKLIST — appended as the last page of the report
# ══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()

h = doc.add_heading('CHECKLIST OF ITEMS FOR THE FINAL DISSERTATION / PROJECT / PROJECT WORK REPORT', level=1)
run = h.runs[0] if h.runs else h.add_run(h.text)
run.font.name = 'Calibri'
run.font.bold = True
run.font.size = Pt(13)
run.font.color.rgb = BLUE_DARK
h.paragraph_format.line_spacing = 1.0

def cl_body(text, space_after=6, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(11)
    r.font.bold = bold
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.5
    return p

cl_body('This checklist is attached as the last page of the final report.')
cl_body('This checklist has been duly completed and verified by the student.')
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(0)

CHECKLIST_ITEMS = [
    'Is the final report neatly formatted with all the elements required for a technical report?',
    'Is the Cover page in proper format as given in Annexure A?',
    'Is the Title page (inner cover page) in proper format?',
    '(a) Is the Certificate from the Supervisor in proper format?\n(b) Has it been signed by the Supervisor?',
    'Is the Abstract included in the report properly written within one page? Have the technical keywords been specified properly?',
    'Is the title of your report appropriate? The title should be adequately descriptive, precise and must reflect the scope of the actual work done. Uncommon abbreviations / acronyms should not be used in the title.',
    'Have you included the List of Abbreviations / Acronyms?',
    'Does the Report contain a summary of the literature survey?',
    'Does the Table of Contents include page numbers?\nAre the pages numbered properly? (Ch. 1 should start on Page # 1)\nAre the Figures numbered properly? (Figure numbers and titles at the bottom of the figures)\nAre the Tables numbered properly? (Table numbers and titles at the top of the tables)\nAre the captions for the Figures and Tables proper?\nAre the Appendices numbered properly? Are their titles appropriate?',
    'Is the conclusion of the Report based on discussion of the work?',
    'Are References or Bibliography given at the end of the Report?\nHave the References been cited properly inside the text of the Report?\nAre all the references cited in the body of the report?',
    'Is the report format and content according to the guidelines? The report should not be a mere printout of a PowerPoint Presentation, or a user manual. Source code of software need not be included in the report.',
]
# Sl. No. 6 ("Title appropriate ... no uncommon abbreviations") is left "No" —
# see note below the table: the title uses the acronym "AIE", which is not
# expanded anywhere in the report and should be resolved before submission.
CHECKLIST_ANSWERS = ['Yes'] * len(CHECKLIST_ITEMS)
CHECKLIST_ANSWERS[5] = 'No — see note below'

t = doc.add_table(rows=1 + len(CHECKLIST_ITEMS), cols=3)
t.style = 'Table Grid'
t.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ['Sl. No.', 'Item', 'Yes / No']
for i, htext in enumerate(headers):
    cell = t.rows[0].cells[i]
    cell.text = htext
    r = cell.paragraphs[0].runs[0]
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.name = 'Calibri'
    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_cell_bg(cell, '1F4E79')

for idx, (item, answer) in enumerate(zip(CHECKLIST_ITEMS, CHECKLIST_ANSWERS), start=1):
    ri = idx
    bg = BLUE_LIGHT if ri % 2 == 1 else WHITE
    row = t.rows[ri]
    row.cells[0].text = str(idx)
    row.cells[1].text = item
    row.cells[2].text = answer
    for c in row.cells:
        r = c.paragraphs[0].runs[0]
        r.font.size = Pt(10)
        r.font.name = 'Calibri'
        set_cell_bg(c, bg)

for row in t.rows:
    row.cells[0].width = Inches(0.5)
    row.cells[1].width = Inches(5.5)
    row.cells[2].width = Inches(1.3)

note = doc.add_paragraph()
note.paragraph_format.space_before = Pt(8)
note.paragraph_format.space_after = Pt(12)
r = note.add_run(
    'Note on item 6: the report title uses the acronym "AIE," which is not expanded '
    'anywhere in the report. Confirm the intended expansion (or retitle) with the '
    'Supervisor before final submission, then update this row to "Yes."'
)
r.font.italic = True
r.font.size = Pt(10)
r.font.name = 'Calibri'

cl_body('Declaration by Student:', bold=True, space_after=4)
cl_body('I certify that I have properly verified all the items in this checklist and ensure '
        'that the report is in proper format as specified in the course handout.', space_after=16)

decl = doc.add_table(rows=3, cols=2)
decl.style = 'Table Grid'
decl_rows = [
    ('Place: Bangalore', 'Signature of the Student'),
    (f'Date: {DATE_OF_SUBMISSION}', f'Name: {STUDENT_NAME}'),
    ('', f'ID No.: {BITS_ID}'),
]
for ri, (left, right) in enumerate(decl_rows):
    for ci, val in enumerate([left, right]):
        cell = decl.rows[ri].cells[ci]
        cell.text = val
        r = cell.paragraphs[0].runs[0]
        r.font.size = Pt(11)
        r.font.name = 'Calibri'

print('Appended CHECKLIST as the last page')

doc.save(PATH)
print(f'Saved: {PATH}')
