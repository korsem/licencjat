import io
import os

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import fonts
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404

from you_train_api.calendar_methods import get_polish_day_of_week
from you_train_api.models import Workout, TrainingPlan, WorkoutInPlan

# to avoid '\' and  '/' - different for windows and linux
font_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "static",
    "fonts",
    "dejavu_sans",
    "DejaVuSans.ttf",
)
bold_font_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "static",
    "fonts",
    "dejavu_sans",
    "DejaVuSans-Bold.ttf",
)
pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold_font_path))


class BaseTrainingPlanPDF:
    def __init__(self, training_plan):
        self.training_plan = training_plan
        self.styles = self._get_styles()
        self.content = []

    def _get_styles(self):
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="Bold", fontName="DejaVuSans-Bold", spaceAfter=12, leading=14
            )
        )
        styles.add(
            ParagraphStyle(
                name="normal", fontName="DejaVuSans", spaceAfter=12, leading=14
            )
        )
        styles.add(
            ParagraphStyle(
                name="headline",
                fontName="DejaVuSans-Bold",
                fontSize=16,
                alignment=TA_CENTER,
                spaceAfter=20,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Footer", alignment=TA_RIGHT, fontName="DejaVuSans", fontSize=10
            )
        )
        return styles

    def add_header(self):
        self.content.append(
            Paragraph(
                f"Plan Treningowy: {self.training_plan.title}", self.styles["headline"]
            )
        )

        if self.training_plan.description:
            self.content.append(
                Paragraph(
                    f"Opis: {self.training_plan.description}", self.styles["normal"]
                )
            )
        if self.training_plan.goal:
            self.content.append(
                Paragraph(f"Cele: {self.training_plan.goal}", self.styles["normal"])
            )

        self.content.append(Spacer(1, 8))

    def add_footer(self, canvas, doc):
        canvas.saveState()
        footer = Paragraph(
            f'Generated on {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}',
            self.styles["Footer"],
        )
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h + 0.5 * cm)
        canvas.restoreState()

    def build_pdf(self, response):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        doc.build(
            self.content, onFirstPage=self.add_footer, onLaterPages=self.add_footer
        )
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)


class CyclicTrainingPlanPDF(BaseTrainingPlanPDF):

    def add_header(self):
        super().add_header()

        start_date = self.training_plan.workout_plan.start_date
        cycle_length = self.training_plan.workout_plan.cycle_length
        end_date = start_date + timedelta(weeks=cycle_length)

        self.content.append(
            Paragraph(
                f'Plan ważny od: {start_date.strftime("%d-%m-%Y")} do: {end_date.strftime("%d-%m-%Y")}',
                self.styles["normal"],
            )
        )
        self.content.append(
            Paragraph(
                f"Ilość tygodni trwania planu: {cycle_length}", self.styles["normal"]
            )
        )
        self.content.append(Spacer(1, 12))

    def add_workouts(self):
        # tworzenie tabeli 2x7 z dniami tygodnia i odpowiadającymi im treningami
        days_of_week = [get_polish_day_of_week(i) for i in range(7)]
        workouts_in_week = [""] * 7

        workouts = WorkoutInPlan.objects.filter(
            workout_plan__training_plan=self.training_plan
        ).order_by("day_of_week")
        for workout_in_plan in workouts:
            day_index = workout_in_plan.day_of_week
            title = workout_in_plan.workout.title
            workouts_in_week[day_index] = Paragraph(title, self.styles["normal"])

        data = [days_of_week, workouts_in_week]

        available_width = A4[0] - 3 * cm
        col_widths = [available_width * 0.15] * 7

        table = Table(data, colWidths=col_widths)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("WORDWRAP", (0, 1), (-1, -1), True),
                ]
            )
        )

        self.content.append(table)
        self.content.append(Spacer(1, 16))

        self.content.append(
            Paragraph("szczegóły treningów:", self.styles["Bold"])
        )  # tu powinien być większa czcionka

        # szczegółowe info
        for workout_in_plan in workouts:
            workout = workout_in_plan.workout

            self.content.append(
                Paragraph(
                    f"Workout: {workout.title} - {get_polish_day_of_week(workout_in_plan.day_of_week)}",
                    self.styles["Bold"],
                )
            )

            if (segment_numb := len(workout.segments.all())) > 1:
                # Informacje o segmentach treningu
                for numb, segment in enumerate(workout.segments.all()):
                    self.content.append(Spacer(1, 5))

                    self.content.append(
                        Paragraph(
                            f"Blok treningowy {numb + 1} / {segment_numb} do wykonania {segment.reps} razy",
                            self.styles["normal"],
                        )
                    )
                    if segment.rest_time:
                        self.content.append(
                            Paragraph(
                                f"na {segment.rest_time} przerwy", self.styles["normal"]
                            )
                        )

                    # Informacje o ćwiczeniach w segmencie
                    for exercise in segment.exercises.all():
                        self.content.append(
                            Spacer(1, 6)
                        )  # Dodanie mniejszego odstępu przed ćwiczeniem

                        # Nazwa ćwiczenia z dodatkowym wcięciem
                        self.content.append(
                            Paragraph(
                                f"Exercise: {exercise.name}", self.styles["normal"]
                            )
                        )
            else:
                # jeśli jest tylko jeden segment - to nie wyśweitlaj info o segmencie
                segment = workout.segments.all().first()
                if (reps := segment.reps) > 1:
                    self.content.append(
                        Paragraph(
                            f"Całość do wykonania {reps} razy", self.styles["normal"]
                        )
                    )
                for exercise in segment.exerciseinsegment_set.all():
                    self.content.append(Spacer(1, 6))

                    # jak wykonywać dane ćwiczenie
                    self.content.append(
                        Paragraph(
                            f"Exercise: {exercise.exercise.name}", self.styles["normal"]
                        )
                    )
                    if exercise.reps:
                        self.content.append(
                            Paragraph(
                                f"Powtórzenia: {exercise.reps}", self.styles["normal"]
                            )
                        )
                    if exercise.duration:
                        self.content.append(
                            Paragraph(
                                f"Czas: {exercise.duration}", self.styles["normal"]
                            )
                        )
                    self.content.append(
                        Paragraph(
                            f"Przerwa: {exercise.rest_time}", self.styles["normal"]
                        )
                    )

            # odstęp po każdyum treningu
            self.content.append(Spacer(1, 12))


class NonCyclicTrainingPlanPDF(BaseTrainingPlanPDF):
    def add_header(self):
        super().add_header()

        start_date = self.training_plan.workout_plan.start_date
        end_date = self.training_plan.workout_plan.end_date

        self.content.append(
            Paragraph(
                f'Plan ważny od: {start_date.strftime("%d-%m-%Y")} do: {end_date.strftime("%d-%m-%Y")}',
                self.styles["normal"],
            )
        )
        self.content.append(Spacer(1, 12))

    def add_workouts(self):
        workouts = WorkoutInPlan.objects.filter(
            workout_plan__training_plan=self.training_plan
        ).order_by("date")
        for workout_in_plan in workouts:
            workout = workout_in_plan.workout
            self.content.append(
                Paragraph(f"Workout: {workout.title}", self.styles["Bold"])
            )
            self.content.append(
                Paragraph(f"Date: {workout_in_plan.date}", self.styles["normal"])
            )
            for segment in workout.segments.all():
                if segment.reps:
                    self.content.append(
                        Paragraph(
                            f"Segment Reps: {segment.reps}", self.styles["normal"]
                        )
                    )
                if segment.rest_time:
                    self.content.append(
                        Paragraph(
                            f"Rest Time: {segment.rest_time}", self.styles["normal"]
                        )
                    )
                self.content.append(Spacer(1, 12))

                for exercise in segment.exerciseinsegment_set.all():
                    self.content.append(Spacer(1, 6))

                    self.content.append(
                        Paragraph(
                            f"Exercise: {exercise.exercise.name}", self.styles["normal"]
                        )
                    )
                    if exercise.reps:
                        self.content.append(
                            Paragraph(
                                f"Powtórzenia: {exercise.reps}", self.styles["normal"]
                            )
                        )
                    if exercise.duration:
                        self.content.append(
                            Paragraph(
                                f"Czas: {exercise.duration}", self.styles["normal"]
                            )
                        )
                    self.content.append(
                        Paragraph(
                            f"Przerwa: {exercise.rest_time}", self.styles["normal"]
                        )
                    )

            self.content.append(Spacer(1, 12))


def generate_training_plan_pdf(request, training_plan_id):
    plan = get_object_or_404(TrainingPlan, id=training_plan_id, user=request.user)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="plan_treningowy_{plan.title}.pdf"'
    )

    if plan.workout_plan.is_cyclic:
        pdf_generator = CyclicTrainingPlanPDF(plan)
    else:
        pdf_generator = NonCyclicTrainingPlanPDF(plan)

    pdf_generator.add_header()
    pdf_generator.add_workouts()
    pdf_generator.build_pdf(response)

    return response
