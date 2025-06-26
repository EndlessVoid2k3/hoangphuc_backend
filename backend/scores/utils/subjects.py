class Subject:
    ALL = {
        "toan": "Math",
        "ngu_van": "Literature",
        "ngoai_ngu": "Foreign Language",
        "vat_li": "Physics",
        "hoa_hoc": "Chemistry",
        "sinh_hoc": "Biology",
        "lich_su": "History",
        "dia_li": "Geography",
        "gdcd": "Civic Education",
    }

    @classmethod
    def all_keys(cls):
        return list(cls.ALL.keys())

    @classmethod
    def get_label(cls, key):
        return cls.ALL.get(key, key)