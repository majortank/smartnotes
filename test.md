```python
class Notes(models.Model):
    CATEGORY_CHOICES = [
        ('Personal', 'Personal'),
        ('Work', 'Work'),
        ('School/Education', 'School/Education'),
        ('Shopping', 'Shopping'),
        ('Travel', 'Travel'),
        ('Recipes', 'Recipes'),
        ('Health/Fitness', 'Health/Fitness'),
        ('Finance', 'Finance'),
        ('Projects', 'Projects'),
        ('Ideas', 'Ideas'),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='Personal',
    )

    # rest of your fields...

```