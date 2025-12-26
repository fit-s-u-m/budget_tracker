CATEGORY_KEYWORDS = {
    "food": ["lunch", "dinner", "restaurant", "meal", "coffee","drink","food"],
    "transport": ["taxi", "bus", "ride", "train", "fuel", "gas","transport"],
    "shopping": ["mall", "clothes", "shoes", "electronics","shopping"],
    "salary": ["salary", "income", "paycheck","salary"],
    "health": ["doctor", "medicine", "hospital", "pharmacy", "clinic", "dentist", "healthcare", "checkup", "therapy", "eyewear","braces","health"],
    "charity": ["donation", "charity", "fundraising", "sponsorship", "contribution","charity"],
    "personal_care": ["haircut", "spa", "salon", "cosmetic", "massage", "skincare", "makeup", "barber"],
    "utilities": ["electricity", "water", "internet", "phone", "mobile", "gas bill", "utility", "broadband","utilities"],
    "housing": ["rent", "mortgage", "apartment", "house", "landlord", "property", "maintenance","house"],
    "entertainment": ["movie", "netflix", "game", "concert","entertainment"],
}
def get_category_from_reason(reason: str) -> str:
    reason_lower = reason.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in reason_lower:
                return category
    return "miscellaneous"

