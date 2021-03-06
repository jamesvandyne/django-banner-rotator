#-*- coding:utf-8 -*-

from random import random

from django.db import models
from django.utils.timezone import now





def pick(bias_list):
    """ Takes a list of 2-tuples [(item, weight)] using weight as the
        probability when calculating an item to choose
    """
    try:
        # First, normalize weights to ensure we
        # have a valid probability distribution
        assert sum([w for i, w in bias_list]) == 1
    except AssertionError:
        norm_const = float(sum([w for i, w in bias_list]))
        distribution = [(i, w / norm_const) for i, w in bias_list]
    else:
        distribution = bias_list

    number = random()
    current = 0.0

    # @link http://fr.w3support.net/index.php?db=so&id=479236
    for choice, probability in distribution:
        current += probability
        if number <= current:
            return choice


class BannerManager(models.Manager):

    def biased_choice(self, place):
        not_finished = models.Q(finish_at__gte=now())
        never_ending = models.Q(finish_at__isnull=True)
        has_started = models.Q(start_at__lte=now())
        queryset = self.filter(not_finished | never_ending, is_active=True, places=place).filter(has_started)

        if not queryset.count():
            raise self.model.DoesNotExist

        normalizer = queryset.aggregate(normalizer=models.Sum('weight'))['normalizer']
        return pick([(i, i.weight / float(normalizer)) for i in queryset])
