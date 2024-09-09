from django.db import models


class Driver(models.Model):
    name = models.CharField(max_length=255)


class ExitReason(models.Model):
    REASON_CHOICES = [
        ('money', 'Money'),
        ('miscommunication', 'Miscommunication'),
        ('other', 'Other'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    reason_category = models.CharField(max_length=50, choices=REASON_CHOICES)
    exit_date = models.DateTimeField(auto_now_add=True)  # When the driver left

    def __str__(self):
        return f"{self.driver.name}"
