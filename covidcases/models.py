from django.db import models

class Case(models.Model):
    caseID = models.IntegerField()
    date = models.DateField()
    city = models.CharField(max_length=100,blank=False)
    locality = models.CharField(max_length=100,blank=False)
    age = models.IntegerField()
    sex = models.CharField(max_length=100,blank=False)
    type = models.CharField(max_length=100,blank=False)
    place = models.CharField(max_length=100,blank=False)
    state = models.CharField(max_length=100,blank=False)

    def __str__(self):
        return '#{} - {}'.format(self.caseID,self.locality)

    class Meta:
        ordering = ['-caseID']
