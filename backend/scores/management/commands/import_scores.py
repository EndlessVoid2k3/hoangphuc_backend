import csv
from django.core.management.base import BaseCommand
from scores.models import Student, SubjectScore
from scores.utils.subjects import Subject
from django.db import transaction

class Command(BaseCommand):
    BATCH_SIZE = 5000

    def handle(self, *args, **kwargs):
        path = "diem_thi_thpt_2024.csv"
        created_students = []
        created_scores = []

        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row_count, row in enumerate(reader, start=1):
                sbd = row.get("sbd")
                if not sbd:
                    continue

                created_students.append(Student(sbd=sbd))
                student_scores = {}

                for subject in Subject.all_keys():
                    raw = row.get(subject)
                    if raw:
                        try:
                            student_scores[subject] = float(raw)
                        except ValueError:
                            continue  # Skip invalid score

                created_scores.append((sbd, student_scores))

                if row_count % self.BATCH_SIZE == 0:
                    self._commit_batch(created_students, created_scores)
                    created_students.clear()
                    created_scores.clear()
                    self.stdout.write(f"Processed {row_count} rows...")

            # Final batch
            self._commit_batch(created_students, created_scores)
            self.stdout.write(self.style.SUCCESS("All rows imported successfully."))

    def _commit_batch(self, student_batch, score_batch):
        # Create students and index by sbd
        Student.objects.bulk_create(student_batch, ignore_conflicts=True, batch_size=self.BATCH_SIZE)
        sbd_to_student = {s.sbd: s for s in Student.objects.filter(sbd__in=[s.sbd for s in student_batch])}

        # Prepare SubjectScore objects
        subject_objs = []
        for sbd, subject_scores in score_batch:
            student = sbd_to_student.get(sbd)
            if not student:
                continue
            for subject, score in subject_scores.items():
                subject_objs.append(SubjectScore(student=student, subject=subject, score=score))

        SubjectScore.objects.bulk_create(subject_objs, batch_size=self.BATCH_SIZE)
