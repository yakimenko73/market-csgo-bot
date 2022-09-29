from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100), ]

JSON_FILE_VALIDATOR = [FileExtensionValidator(allowed_extensions=["json"]), ]
