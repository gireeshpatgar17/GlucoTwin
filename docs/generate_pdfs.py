"""Generate the GlucoTwin architecture brief and 11-slide submission deck."""
from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
METRICS = json.loads((ROOT / "data" / "metrics.json").read_text(encoding="utf-8"))
W, H = landscape(A4)
NAVY = colors.HexColor("#142B45")
BLUE = colors.HexColor("#246B91")
TEAL = colors.HexColor("#16A394")
GOLD = colors.HexColor("#D9A441")
PURPLE = colors.HexColor("#7357A6")
INK = colors.HexColor("#263849")
MUTED = colors.HexColor("#5B7082")
PAPER = colors.HexColor("#F5F8FA")
WHITE = colors.white

BODY = ParagraphStyle("Body", fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK)
SMALL = ParagraphStyle("Small", fontName="Helvetica", fontSize=8.5, leading=11, textColor=MUTED)
SLIDE_BODY = ParagraphStyle("SlideBody", fontName="Helvetica", fontSize=16, leading=23, textColor=INK)
SLIDE_SMALL = ParagraphStyle("SlideSmall", fontName="Helvetica", fontSize=11, leading=16, textColor=INK)


def draw_node(c, x, y, w, h, title, lines, color):
    c.setFillColor(WHITE)
    c.setStrokeColor(color)
    c.setLineWidth(1.4)
    c.roundRect(x, y, w, h, 9, fill=1, stroke=1)
    c.setFillColor(color)
    c.roundRect(x, y + h - 8, w, 8, 4, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 10, y + h - 23, title)
    c.setFillColor(INK)
    c.setFont("Helvetica", 8.1)
    line_y = y + h - 38
    for line in lines:
        c.drawString(x + 10, line_y, line)
        line_y -= 11


def arrow(c, points, color=BLUE, dashed=False):
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.4)
    if dashed:
        c.setDash(4, 3)
    path = c.beginPath()
    path.moveTo(*points[0])
    for point in points[1:]:
        path.lineTo(*point)
    c.drawPath(path, stroke=1, fill=0)
    c.setDash()
    (x1, y1), (x2, y2) = points[-2], points[-1]
    if x2 > x1:
        tri = [(x2, y2), (x2-7, y2+3.5), (x2-7, y2-3.5)]
    elif x2 < x1:
        tri = [(x2, y2), (x2+7, y2+3.5), (x2+7, y2-3.5)]
    elif y2 > y1:
        tri = [(x2, y2), (x2-3.5, y2-7), (x2+3.5, y2-7)]
    else:
        tri = [(x2, y2), (x2-3.5, y2+7), (x2+3.5, y2+7)]
    p = c.beginPath()
    p.moveTo(*tri[0])
    p.lineTo(*tri[1])
    p.lineTo(*tri[2])
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def draw_architecture(c, x, y, scale=1):
    c.saveState()
    c.translate(x, y)
    c.scale(scale, scale)
    draw_node(c, 8, 255, 152, 70, "SYNTHETIC EHR STREAM",
              ["60 fictional profiles", "Age, BMI, HbA1c, duration"], TEAL)
    draw_node(c, 8, 112, 152, 82, "SIMULATED SENSOR STREAM",
              ["15-minute readings", "Glucose, heart rate, activity", "Sleep and time features"], TEAL)
    draw_node(c, 218, 210, 148, 82, "PREPROCESSING",
              ["Validate timestamps", "Sort and check cadence", "Align glucose at +8 rows"], GOLD)
    draw_node(c, 405, 210, 137, 82, "FEATURE GENERATION",
              ["Current row only", "Sensor + profile fields", "No future sensor rows"], BLUE)
    draw_node(c, 580, 210, 115, 82, "PREDICTION MODEL",
              ["HistGradientBoosting", "Glucose at t + 120 min"], PURPLE)
    draw_node(c, 580, 72, 115, 78, "VIRTUAL PATIENT STATE",
              ["Selected profile", "Current cursor + values"], GOLD)
    draw_node(c, 370, 72, 165, 78, "STREAMLIT DASHBOARD",
              ["Profile and sensor history", "Forecast and measured MAE", "Advance stream by 15 min"], BLUE)
    arrow(c, [(160, 290), (190, 290), (190, 263), (218, 263)], TEAL)
    arrow(c, [(160, 151), (190, 151), (190, 238), (218, 238)], TEAL)
    arrow(c, [(366, 251), (405, 251)], GOLD)
    arrow(c, [(542, 251), (580, 251)], BLUE)
    arrow(c, [(637, 210), (637, 150)], PURPLE)
    arrow(c, [(580, 111), (535, 111)], GOLD)
    arrow(c, [(370, 88), (315, 88), (315, 35), (82, 35), (82, 112)], TEAL, dashed=True)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(195, 28, "Dashboard control advances the simulated sensor clock by one 15-minute step")
    c.restoreState()


class ArchitectureDiagram(Flowable):
    def __init__(self, width=700, height=335):
        super().__init__()
        self.width, self.height = width, height

    def draw(self):
        draw_architecture(self.canv, 0, 0, self.width / 700)


def arch_footer(c, doc):
    c.saveState()
    c.setStrokeColor(colors.HexColor("#D8E2E9"))
    c.line(25*mm, 13*mm, W-25*mm, 13*mm)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(25*mm, 8*mm, "GLUCOTWIN  |  SYNTHETIC DATA  |  NOT FOR CLINICAL USE")
    c.drawRightString(W-25*mm, 8*mm, str(doc.page))
    c.restoreState()


def build_architecture():
    path = OUT / "architecture.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=landscape(A4),
                            rightMargin=25*mm, leftMargin=25*mm,
                            topMargin=15*mm, bottomMargin=21*mm,
                            title="GlucoTwin Architecture")
    title = ParagraphStyle("ArchTitle", fontName="Helvetica-Bold", fontSize=24,
                           leading=29, textColor=NAVY, spaceAfter=4)
    sub = ParagraphStyle("ArchSub", fontName="Helvetica", fontSize=10.5,
                         leading=14, textColor=BLUE, spaceAfter=7)
    story = [Paragraph("GlucoTwin | System Architecture", title),
             Paragraph("Local synthetic two-hour glucose forecasting proof of concept", sub),
             ArchitectureDiagram(width=700, height=335), Spacer(1, 5)]
    metrics = ParagraphStyle("MetricLine", fontName="Helvetica-Bold", fontSize=10,
                             leading=14, textColor=NAVY, alignment=TA_LEFT)
    story.append(Paragraph(
        f"Measured run: {METRICS['model']} | train {METRICS['train_rows']:,} | test {METRICS['test_rows']:,} | "
        f"model MAE {METRICS['model_mae_mg_dl']:.3f} mg/dL | persistence MAE "
        f"{METRICS['baseline_last_value_mae_mg_dl']:.3f} mg/dL", metrics))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Leakage control: training labels are purged so every training target timestamp precedes the test cutoff. "
        "At inference, the model receives only the selected patient profile and the current simulated sensor row. "
        "No real patient data or clinical validation are included.", BODY))
    doc.build(story, onFirstPage=arch_footer, onLaterPages=arch_footer)
    return path


def para(c, text, x, top, width, style=SLIDE_BODY):
    p = Paragraph(text, style)
    _, height = p.wrap(width, H)
    p.drawOn(c, x, top-height)
    return height


def bullets(c, items, x, top, width, font=SLIDE_BODY, gap=12):
    y = top
    for item in items:
        c.setFillColor(TEAL)
        c.roundRect(x, y-10, 7, 7, 2, fill=1, stroke=0)
        height = para(c, item, x+20, y, width-20, font)
        y -= height + gap
    return y


def slide_base(c, n, title, kicker=None, dark=False):
    c.setFillColor(NAVY if dark else PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    if dark:
        c.setFillColor(TEAL)
        c.rect(0, 0, 11, H, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(11, 0, 3, H, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 27)
        c.drawString(48, H-62, title)
        if kicker:
            c.setFillColor(colors.HexColor("#B8CDD8"))
            c.setFont("Helvetica", 13)
            c.drawString(50, H-91, kicker)
    else:
        c.setFillColor(TEAL)
        c.rect(0, H-9, W, 9, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 23)
        c.drawString(48, H-57, title)
        if kicker:
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 11)
            c.drawString(50, H-81, kicker)
        c.setStrokeColor(colors.HexColor("#D9E2E8"))
        c.line(48, 42, W-48, 42)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(48, 27, "Synthetic data only | No clinical validation")
        c.drawRightString(W-48, 27, f"{n:02d} / 11")


def metric(c, x, y, label, value, color=BLUE):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, label.upper())
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 23)
    c.drawString(x, y-30, value)


def draw_slide(c, number, title, subtitle, body, mode="bullets"):
    slide_base(c, number, title, subtitle)
    if mode == "bullets":
        bullets(c, body, 60, H-125, W-120)
    c.showPage()


def build_presentation():
    path = OUT / "presentation.pdf"
    c = canvas.Canvas(str(path), pagesize=landscape(A4), pageCompression=1)
    c.setTitle("GlucoTwin | Digital Twin Challenge 2026")
    c.setAuthor("GlucoTwin team - details pending")

    # 1. Title
    slide_base(c, 1, "GlucoTwin", "Digital Twin Challenge 2026 | Two-hour synthetic glucose forecast", dark=True)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, H-155, "A reproducible digital twin proof of concept")
    c.setFillColor(colors.HexColor("#D7E5EC"))
    c.setFont("Helvetica", 13)
    c.drawString(50, H-187, "Team: [Add team member names]    College: [Add institution]")
    c.drawString(50, H-213, "Contact: [Add supplied contact details]")
    c.setFillColor(TEAL)
    c.roundRect(50, 95, 430, 55, 12, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(265, 116, "Synthetic data only. Not for clinical use.")
    c.setFillColor(colors.HexColor("#B8CDD8"))
    c.setFont("Helvetica", 10)
    c.drawRightString(W-48, 28, "01 / 11")
    c.showPage()

    # 2. Problem
    slide_base(c, 2, "The prediction problem", "Can the current virtual patient state inform a two-hour forecast?")
    bullets(c, [
        "People with Type 2 diabetes need ongoing glucose monitoring. This prototype explores a forecasting workflow, not a clinical intervention.",
        "The defined target is sensor glucose in mg/dL exactly 120 minutes after the current timestamp.",
        "At a 15-minute cadence, the label is the eighth subsequent sensor reading.",
        "The dashboard makes the prediction horizon visible beside the current simulated reading."], 60, H-125, W-120)
    c.setStrokeColor(BLUE); c.setLineWidth(2)
    c.line(120, 105, W-120, 105)
    c.setFillColor(BLUE); c.circle(120, 105, 6, fill=1, stroke=0); c.circle(W-120, 105, 6, fill=1, stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 11)
    c.drawString(100, 84, "t: current sensor state")
    c.drawRightString(W-100, 84, "t + 120 min: prediction target")
    c.showPage()

    # 3. Healthcare use case
    slide_base(c, 3, "Healthcare use case", "A research-facing interface concept for review of trends")
    bullets(c, [
        "A synthetic patient profile supplies age, BMI, HbA1c, diabetes duration, and a medication category.",
        "A simulated sensor stream supplies glucose, heart rate, activity, sleep flag, and time-of-day features.",
        "A reviewer can change patient, advance the virtual time, and compare a forecast with the current state.",
        "A future governed study could evaluate whether such forecasts add value to a care workflow. This demo does not test that clinical question."], 60, H-130, W-120)
    c.showPage()

    # 4. Existing gap
    slide_base(c, 4, "The gap this prototype addresses", "A reproducible engineering workflow, with its evidence boundary made explicit")
    left = ["A stated two-hour label", "Time-ordered evaluation", "Current-state prediction inputs", "Visible synthetic / prediction labels"]
    right = ["Target horizon can be ambiguous", "Random splits can hide time leakage", "Forecasts can accidentally see later rows", "Simulated values can be mistaken for observations"]
    c.setFillColor(BLUE); c.setFont("Helvetica-Bold", 12); c.drawString(62, H-135, "Prototype controls")
    c.setFillColor(MUTED); c.drawString(450, H-135, "Failure mode avoided")
    y = H-175
    for a, b in zip(left, right):
        c.setFillColor(TEAL); c.circle(70, y+4, 4, fill=1, stroke=0)
        para(c, a, 84, y+12, 310, SLIDE_SMALL)
        c.setFillColor(GOLD); c.circle(455, y+4, 4, fill=1, stroke=0)
        para(c, b, 470, y+12, 315, SLIDE_SMALL)
        y -= 55
    para(c, "This describes the engineering gap addressed by this submission. It is not a comparison with named commercial or clinical systems.", 62, 90, 700, SMALL)
    c.showPage()

    # 5. Architecture
    slide_base(c, 5, "Architecture", "Two local synthetic streams feed a time-aligned forecast")
    draw_architecture(c, 68, 80, 1.0)
    c.showPage()

    # 6. Data
    slide_base(c, 6, "Synthetic data", "Seeded and local. No real EHR or device data are used.")
    metric(c, 70, H-150, "Profiles", "60", TEAL)
    metric(c, 300, H-150, "Sensor samples", "120,960", BLUE)
    metric(c, 545, H-150, "Cadence", "15 min", PURPLE)
    metric(c, 70, H-265, "Coverage", "21 days", GOLD)
    metric(c, 300, H-265, "Patient records", "Synthetic EHR", TEAL)
    metric(c, 545, H-265, "Sensor fields", "5 + time", BLUE)
    para(c, "Profile fields include age, sex, BMI, HbA1c, duration, and medication category. Sensor fields include glucose, heart rate, activity, sleep, and cyclic time features.", 70, 125, 700, SLIDE_SMALL)
    c.showPage()

    # 7. Target and feature controls
    slide_base(c, 7, "Target, features and leakage controls", "The model sees the present row, while evaluation respects time")
    bullets(c, [
        "Label: glucose at t + 120 minutes, aligned by shifting eight records within each patient stream.",
        "Input features: current glucose, heart rate, activity, sleep, time-of-day, age, BMI, HbA1c, and diabetes duration.",
        "The inference helper selects only those columns from the selected current row and patient profile.",
        "The chronological holdout reserves later timestamps for testing and purges training rows whose target reaches the test cutoff."], 60, H-130, W-120)
    c.setFillColor(TEAL); c.setFont("Helvetica-Bold", 12)
    c.drawString(62, 79, "No future sensor rows are passed to the inference feature builder.")
    c.showPage()

    # 8. Model
    slide_base(c, 8, "Model and baseline", "A local scikit-learn regressor compared with persistence")
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 16)
    c.drawString(65, H-145, METRICS["model"])
    para(c, "HistGradientBoostingRegressor fitted on the earlier portion of the pooled timeline. The saved artifact contains the model, feature names, and evaluation metrics.", 65, H-165, 680, SLIDE_BODY)
    c.setFillColor(BLUE); c.setFont("Helvetica-Bold", 13)
    c.drawString(65, H-280, "Baseline")
    para(c, "Predict the two-hour glucose target using the current glucose value unchanged. This simple persistence baseline is evaluated on the same held-out rows.", 65, H-300, 680, SLIDE_BODY)
    c.setFillColor(MUTED); c.setFont("Helvetica", 10)
    c.drawString(65, 86, "No hyperparameter search or clinical calibration is claimed.")
    c.showPage()

    # 9. Evaluation
    slide_base(c, 9, "Measured evaluation", "One reproducible synthetic run. No clinical validation.")
    metric(c, 85, H-175, "Model MAE", f"{METRICS['model_mae_mg_dl']:.3f} mg/dL", TEAL)
    metric(c, 440, H-175, "Persistence MAE", f"{METRICS['baseline_last_value_mae_mg_dl']:.3f} mg/dL", BLUE)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 12)
    c.drawString(85, H-260, "Chronological split")
    details = [
        f"Train: {METRICS['train_rows']:,} rows",
        f"Test: {METRICS['test_rows']:,} later rows",
        f"Cutoff: {METRICS['cutoff_utc']}",
        "120-minute label purge before test boundary"]
    bullets(c, details, 85, H-285, 650, SLIDE_SMALL, gap=9)
    para(c, "Synthetic-data MAE is not evidence of real-world accuracy, safety, benefit, or generalization.", 85, 90, 670, SMALL)
    c.showPage()

    # 10. Dashboard demo evidence
    slide_base(c, 10, "Dashboard demonstration", "Actual Streamlit AppTest state transitions, not a mock screenshot")
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 12)
    headers = ["Interaction", "Current glucose", "Prediction at +2h", "Stream cursor"]
    xs = [66, 270, 430, 605]
    for x, text in zip(xs, headers): c.drawString(x, H-142, text)
    c.setStrokeColor(colors.HexColor("#D8E2E9")); c.line(64, H-155, W-64, H-155)
    rows = [
        ("SYN-001 initial", "95 mg/dL", "95.0 mg/dL", "00:00 UTC"),
        ("Advance 15 min", "97 mg/dL", "95.2 mg/dL", "00:15 UTC"),
        ("Select SYN-002", "129 mg/dL", "131.2 mg/dL", "00:00 UTC")]
    y = H-190
    for row in rows:
        for x, text in zip(xs, row):
            c.setFillColor(TEAL if x == xs[0] else INK)
            c.setFont("Helvetica-Bold" if x == xs[0] else "Helvetica", 11)
            c.drawString(x, y, text)
        y -= 42
    c.setFillColor(INK); c.setFont("Helvetica", 11)
    c.drawString(66, 125, "Verified: app renders without exceptions; selecting and advancing the stream recomputes the forecast.")
    c.setFillColor(MUTED); c.setFont("Helvetica-Oblique", 9)
    c.drawString(66, 103, "A browser screenshot was unavailable in this run, so no screenshot or UI mock is presented.")
    c.showPage()

    # 11. Limitations / future work
    slide_base(c, 11, "Limits, next steps and submission status", "A prototype for research discussion, not a care tool")
    bullets(c, [
        "All profiles, sensor readings, and metrics are generated. The simulator is simplified and unvalidated.",
        "No prospective, external, subgroup, safety, fairness, or clinical validation has been performed.",
        "Next: confirm challenge protocol, obtain appropriate governance and consent, validate on suitable data, and assess subgroup performance before any clinical research claim.",
        "Demo video: pending real recording and upload. Team and institution details remain placeholders."], 60, H-130, W-120, SLIDE_SMALL, gap=9)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 13)
    c.drawString(60, 75, "MIT licensed | Full setup, model results, and limitations are in README.md")
    c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    print(f"Created {build_architecture()}")
    print(f"Created {build_presentation()}")
