from datetime import datetime
from app.models.issue import Issue
from app.models.issue_duplicate import IssueDuplicate


class IssueDuplicateService:

    @staticmethod
    def mark_as_duplicate(original_issue_id: str, duplicate_issue_id: str) -> IssueDuplicate:

        original = Issue.objects.get(id=original_issue_id)
        duplicate = Issue.objects.get(id=duplicate_issue_id)

        duplicate_record = IssueDuplicate(
            original_issue=original,
            duplicate_issue=duplicate,
            status='pending'
        )
        duplicate_record.save()
        return duplicate_record

    @staticmethod
    def merge_duplicates(
        duplicate_id: str,
        merged_by_user_id: str,
        fields_to_merge: list = None
    ) -> IssueDuplicate:

        if fields_to_merge is None:
            fields_to_merge = ['description', 'contact_phone', 'media']

        duplicate_record = IssueDuplicate.objects.get(id=duplicate_id)

        if duplicate_record.status != 'pending':
            raise ValueError(f"Cannot merge duplicate with status: {duplicate_record.status}")

        original = duplicate_record.original_issue
        duplicate = duplicate_record.duplicate_issue

        for field in fields_to_merge:
            if field == 'description':
                if duplicate.description and not original.description:
                    original.description = duplicate.description
            elif field == 'contact_phone':
                if duplicate.contact_phone and not original.contact_phone:
                    original.contact_phone = duplicate.contact_phone
            elif field == 'media':
                if duplicate.media:
                    original.media.extend(duplicate.media)
            elif field == 'options':
                if duplicate.options:
                    original.options.extend(duplicate.options)
            elif field == 'animal_count':
                if duplicate.animal_count and duplicate.animal_count > original.animal_count:
                    original.animal_count = duplicate.animal_count

        original.updated_at = datetime.utcnow()
        original.save()

        duplicate.status = 'duplicate'
        duplicate.duplicate_of = original
        duplicate.updated_at = datetime.utcnow()
        duplicate.save()

        if original.duplicates is None:
            original.duplicates = []
        original.duplicates.append(duplicate)
        original.save()

        duplicate_record.status = 'merged'
        duplicate_record.merged_fields = fields_to_merge
        duplicate_record.merged_by_id = merged_by_user_id
        duplicate_record.merged_at = datetime.utcnow()
        duplicate_record.save()

        return duplicate_record

    @staticmethod
    def reject_duplicate(duplicate_id: str, reason: str = None) -> IssueDuplicate:
        duplicate_record = IssueDuplicate.objects.get(id=duplicate_id)

        if duplicate_record.status != 'pending':
            raise ValueError(f"Can only reject pending duplicates, current status: {duplicate_record.status}")

        duplicate_record.status = 'rejected'
        duplicate_record.rejection_reason = reason
        duplicate_record.save()

        return duplicate_record

    @staticmethod
    def get_duplicates_for_issue(issue_id: str) -> list:
        return IssueDuplicate.objects(
            original_issue_id=issue_id
        ).all()

    @staticmethod
    def get_pending_duplicates() -> list:
        return IssueDuplicate.objects(status='pending').all()
