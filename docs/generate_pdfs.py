"""Generate the architecture brief and short challenge presentation PDFs."""
import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
metrics = json.loads((ROOT / "data" / "metrics.json").read_text(encoding="utf-8"))
NAVY, BLUE = colors.HexColor("#12243A"), colors.HexColor("#176B87")
PALE, INK = colors.HexColor("#EEF5F7"), colors.HexColor("#243447")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Hero", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=27, leading=32, textColor=NAVY, spaceAfter=12))
styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=12, leading=17, textColor=BLUE, spaceAfter=12))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontSize=16, leading=20, textColor=NAVY, spaceBefore=9, spaceAfter=7))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=10, leading=15, textColor=INK, spaceAfter=7))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontSize=8, leading=11, textColor=INK))
styles.add(ParagraphStyle(name="Headx", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=colors.white))
styles.add(ParagraphStyle(name="SlideTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=28, leading=34, textColor=NAVY, alignment=TA_LEFT, spaceAfter=13))

def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])

def footer(canvas, doc):
    canvas.saveState()
    w, _ = doc.pagesize
    canvas.setStrokeColor(colors.HexColor("#D8E3E8"))
    canvas.line(18*mm, 15*mm, w-18*mm, 15*mm)
    canvas.setFillColor(BLUE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18*mm, 10*mm, "GLUCOTWIN  |  SYNTHETIC DATA  |  NOT FOR CLINICAL USE")
    canvas.drawRightString(w-18*mm, 10*mm, str(doc.page))
    canvas.restoreState()

def table(rows, widths, font=10):
    formatted = [[P(str(cell), "Headx" if r == 0 else "Smallx") for cell in row] for r, row in enumerate(rows)]
    t = Table(formatted, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(0,1),(-1,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,-1),font),("LEADING",(0,0),(-1,-1),font+4),
        ("BACKGROUND",(0,1),(-1,-1),PALE),("GRID",(0,0),(-1,-1),.5,colors.white),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),9),
        ("RIGHTPADDING",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    return t

arch = SimpleDocTemplate(str(OUT/"architecture.pdf"), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=18*mm, bottomMargin=23*mm, title="GlucoTwin Architecture")
story = [P("GlucoTwin", "Hero"), P("Architecture brief | Digital Twin Challenge 2026", "Sub"),
    P("Purpose and boundary", "H2x"), P("A local proof of concept forecasts synthetic glucose values two hours ahead using fictional patient context and a simulated 15-minute sensor stream. The software is for engineering demonstration and education only; no real patient records, clinical validation, or treatment recommendations are included."),
    P("Data flow", "H2x"), table([["Stage","What happens","Artifact"],
        ["Generate","Seeded fictional demographics, BMI, HbA1c and time series; glucose, heart rate, activity, sleep and cyclic time features.","patients.csv<br/>sensor_readings.csv"],
        ["Align","Sort each patient stream, require exact 15-minute intervals, and shift glucose eight samples to form t + 120 min target.","training frame"],
        ["Evaluate","Chronological pooled-time holdout with latest 20% test and a 120-minute purge so training targets stay before the test boundary.","metrics.json"],
        ["Serve","Streamlit selects a synthetic patient, advances the virtual stream, builds features and displays a local model estimate.","app.py"],
        ["Review","Tests cover deterministic generation, horizon alignment, chronological training and invalid cadence.","tests/" ]], [27*mm,91*mm,48*mm], 8),
    P("Model and measured synthetic run", "H2x"), P(f"Target: glucose (mg/dL) at t + 120 minutes. This checked-in run used {metrics['model']}, with {metrics['train_rows']:,} training rows and {metrics['test_rows']:,} test rows. Model MAE: {metrics['model_mae_mg_dl']:.3f} mg/dL. Last-value baseline MAE: {metrics['baseline_last_value_mae_mg_dl']:.3f} mg/dL. Split cutoff: {metrics['cutoff_utc']}. A 120-minute purge prevents training labels from crossing the cutoff. These figures reflect only the synthetic generator."),
    P("Reproducibility and limitations", "H2x"), P("Run python generate_data.py, python train_model.py, then streamlit run app.py. A seeded NumPy ridge fallback writes the artifact in offline environments; with declared dependencies installed, training uses scikit-learn HistGradientBoostingRegressor and joblib. The exact model choice is recorded in metrics. Synthetic distributions do not establish real-world accuracy, safety, equity, or usefulness. Do not use for patient care."),
    P("System requirements", "H2x"), P("Python with pandas, NumPy, scikit-learn, Streamlit, Plotly, pytest and joblib. The offline fallback additionally uses the Python standard library. No cloud services or external health-data connections.")]
arch.build(story, onFirstPage=footer, onLaterPages=footer)

pres = SimpleDocTemplate(str(OUT/"presentation.pdf"), pagesize=landscape(A4), rightMargin=25*mm, leftMargin=25*mm, topMargin=20*mm, bottomMargin=24*mm, title="GlucoTwin Challenge Presentation")
slides = []
def slide(title, subtitle, bullets, rows=None):
    slides.extend([P(title,"SlideTitle"),P(subtitle,"Sub")])
    for item in bullets:
        slides.extend([P("-  "+item,"Bodyx"),Spacer(1,5)])
    if rows:
        slides.extend([Spacer(1,8),table(rows,[59*mm,59*mm,59*mm],11)])

slide("GlucoTwin","A local synthetic digital twin for a two-hour glucose forecast",[
    "Digital Twin Challenge 2026 | Team: [Add team name] | College: [Add institution]",
    "A proof of concept for exploring patient context plus a simulated sensor stream.",
    "All people and observations are fictional. Not for clinical use."])
slides.append(PageBreak())
slide("The use case","Could patient-specific context help estimate glucose two hours ahead?",[
    "Forecast target is glucose at current timestamp + 120 minutes.",
    "A future governed research workflow could inspect trends and forecasting concepts.",
    "This prototype is not a medical device and does not support diagnosis or treatment."])
slides.append(PageBreak())
slide("Data and model","Seeded generation makes the complete demo reproducible",[
    "60 synthetic EHR-style profiles; 120,960 simulated readings at 15-minute intervals.",
    "Features: glucose, heart rate, activity, sleep, time-of-day, age, BMI, HbA1c and duration.",
    "Chronological holdout with a 120-minute purge: training labels stay before the later test timestamps."],
    [["Model MAE","Baseline MAE","Test rows"],[f"{metrics['model_mae_mg_dl']:.3f} mg/dL",f"{metrics['baseline_last_value_mae_mg_dl']:.3f} mg/dL",f"{metrics['test_rows']:,}"]])
slides.append(PageBreak())
slide("Live demo","Streamlit dashboard and virtual patient state",[
    "Choose a synthetic patient and inspect fictional profile fields.",
    "Advance the simulated sensor stream one 15-minute record at a time.",
    "Read the current simulated value separately from the predicted value at +2 hours.",
    "Metrics are actual checked-in synthetic evaluation, not clinical validation."])
slides.append(PageBreak())
slide("Limits and next steps","Responsible interpretation comes first",[
    "Synthetic physiology is simplified and does not represent device noise or patient diversity.",
    "No external, prospective, subgroup, or clinical validation has been performed.",
    "Before clinical research: governance, consent, data quality, external validation, safety, and fairness review.",
    "Demo video: [Add a real recording link after it exists]."])
pres.build(slides, onFirstPage=footer, onLaterPages=footer)
print("Generated architecture.pdf and presentation.pdf")
