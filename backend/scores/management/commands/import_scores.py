import csv
from django.core.management.base import BaseCommand
from scores.models import Student, SubjectScore
from scores.utils.subjects import Subject
from django.db import transaction

class Command(BaseCommand):

    BATCH_SIZE = 500

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

                student = Student(sbd=sbd)
                created_students.append(student)

                for subject in Subject.all_keys():
                    raw = row.get(subject)
                    if raw:
                        try:
                            score = float(raw)
                            created_scores.append((sbd, subject, score))
                        except ValueError:
                            self.stderr.write(f"Invalid score {raw} for {sbd} - {subject}")

                # Commit every BATCH_SIZE rows
                if row_count % self.BATCH_SIZE == 0:
                    self._commit_batch(created_students, created_scores)
                    created_students.clear()
                    created_scores.clear()
                    self.stdout.write(f"Processed {row_count} rows...")

            # Final batch
            self._commit_batch(created_students, created_scores)
            self.stdout.write(self.style.SUCCESS("All rows imported successfully."))

    def _commit_batch(self, student_batch, score_batch):
        student_objs = Student.objects.bulk_create(student_batch, ignore_conflicts=True, batch_size=self.BATCH_SIZE)

        sbd_to_student = {sbd: Student.objects.get(sbd=sbd) for sbd in [s.sbd for s in student_batch]}
        subject_objs = [
            SubjectScore(student=sbd_to_student[sbd], subject=subj, score=score)
            for sbd, subj, score in score_batch
            if sbd in sbd_to_student
        ]
        SubjectScore.objects.bulk_create(subject_objs, batch_size=self.BATCH_SIZE)
