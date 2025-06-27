import pandas as pd
from tqdm import tqdm
from django.core.management.base import BaseCommand
from scores.models import Student, SubjectScore
from django.db import transaction

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Step 1: Load CSV with Pandas
        df = pd.read_csv("diem_thi_thpt_2024.csv")
        subject_cols = [col for col in df.columns if col not in ["sbd", "ma_ngoai_ngu"]]

        # Step 2: Bulk insert unique students
        unique_sbds = df["sbd"].dropna().astype(str).unique()
        existing_sbds = set(Student.objects.filter(sbd__in=unique_sbds).values_list("sbd", flat=True))
        new_students = [Student(sbd=sbd) for sbd in unique_sbds if sbd not in existing_sbds]

        self.stdout.write(f"Inserting {len(new_students)} new students...")
        Student.objects.bulk_create(new_students, ignore_conflicts=True)

        # Step 3: Fetch full student map (sbd → object)
        student_map = {
            s.sbd: s for s in Student.objects.filter(sbd__in=unique_sbds)
        }

        # Step 4: Build and bulk insert subject scores
        scores_to_create = []
        chunk_size = 10000

        self.stdout.write("Preparing subject scores...")
        for _, row in tqdm(df.iterrows(), total=len(df)):
            sbd = str(row["sbd"])
            student = student_map.get(sbd)
            if not student:
                continue

            for subject in subject_cols:
                raw_score = row.get(subject)
                if pd.notnull(raw_score):
                    try:
                        score = float(raw_score)
                        scores_to_create.append(
                            SubjectScore(student=student, subject=subject, score=score)
                        )
                    except ValueError:
                        continue  # invalid score string

            # Chunk insert every 10k scores
            if len(scores_to_create) >= chunk_size:
                with transaction.atomic():
                    SubjectScore.objects.bulk_create(scores_to_create, ignore_conflicts=True)
                scores_to_create = []

        # Insert any remaining scores
        if scores_to_create:
            with transaction.atomic():
                SubjectScore.objects.bulk_create(scores_to_create, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("Import complete."))