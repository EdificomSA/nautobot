from nautobot.utilities.choices import ChoiceSet


class FeatureChoices(ChoiceSet):

    Yes = "Yes"
    No = "No"
    Other = "Other"

    CHOICES = (
        (Yes, "Yes"),
        (No, "No"),
        (Other, "Other"),
    )