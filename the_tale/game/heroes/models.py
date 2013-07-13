# coding: utf-8
import datetime

from django.db import models

from game.game_info import GENDER
from game.balance.enums import RACE

from game.balance import enums as e


class Hero(models.Model):

    MAX_NAME_LENGTH = 32

    created_at_turn = models.IntegerField(null=False, default=0)
    saved_at_turn = models.IntegerField(null=False, default=0)

    saved_at = models.DateTimeField(auto_now=True, default=datetime.datetime.fromtimestamp(0))

    account = models.ForeignKey('accounts.Account', related_name='heroes', default=None, null=True, blank=True)

    is_fast = models.BooleanField(default=True, db_index=True) # copy from account.is_fast

    is_alive = models.BooleanField(default=True)

    active_state_end_at = models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))
    premium_state_end_at = models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))
    ban_state_end_at = models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))

    # time when ui caching and model saving has started
    ui_caching_started_at = models.DateTimeField(auto_now_add=True, default=datetime.datetime(2000, 1, 1))

    #base
    name = models.CharField(max_length=MAX_NAME_LENGTH, null=False)

    gender = models.IntegerField(null=False, default=GENDER.MASCULINE, choices=GENDER._CHOICES)

    race = models.IntegerField(choices=RACE._CHOICES, default=RACE.HUMAN)

    level = models.IntegerField(null=False, default=1)
    experience = models.FloatField(null=False, default=0)

    # for random.seed, when form next ability choices
    # MUST NOT BE RESETED
    destiny_points_spend = models.IntegerField(null=False, default=0)

    health = models.FloatField(null=False, default=0.0)

    raw_power = models.BigIntegerField(null=False, default=0) # special field for ratings

    money = models.BigIntegerField(null=False, default=0)

    equipment = models.TextField(null=False, default='{}')
    bag = models.TextField(null=False, default='{}')

    abilities = models.TextField(null=False, default='', blank=True)

    quests_history = models.TextField(null=False, default='{}')
    places_history = models.TextField(null=False, default='{}')

    messages = models.TextField(null=False, default='[]')
    diary = models.TextField(null=False, default='[]')

    actions = models.TextField(null=False, default='{}')

    name_forms = models.TextField(null=False, default='', blank=True)

    pvp = models.TextField(null=False, default='{}')

    next_spending = models.IntegerField(null=False, default=e.ITEMS_OF_EXPENDITURE.USELESS, choices=e.ITEMS_OF_EXPENDITURE._CHOICES)

    energy = models.FloatField(null=False, default=0.0)
    last_energy_regeneration_at_turn = models.IntegerField(null=False, default=0)

    might = models.FloatField(null=False, default=0.0)
    might_updated_time = models.DateTimeField(auto_now_add=True, db_index=True, default=datetime.datetime(2000, 1, 1))

    #position
    pos_place = models.ForeignKey('places.Place', related_name='+', null=True, default=None, blank=True)
    pos_road = models.ForeignKey('roads.Road', related_name='+', null=True, default=None, blank=True)
    pos_percents = models.FloatField(null=True, default=None, blank=True)
    pos_invert_direction = models.NullBooleanField(default=False, null=True, blank=True)
    pos_from_x = models.IntegerField(null=True, blank=True, default=None)
    pos_from_y = models.IntegerField(null=True, blank=True, default=None)
    pos_to_x = models.IntegerField(null=True, blank=True, default=None)
    pos_to_y = models.IntegerField(null=True, blank=True, default=None)

    #character
    pref_energy_regeneration_type = models.IntegerField(null=False, default=e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY, choices=e.ANGEL_ENERGY_REGENERATION_TYPES._CHOICES, blank=True)
    pref_energy_regeneration_type_changed_at = models.DateTimeField(default=datetime.datetime(2000, 1, 1))

    pref_mob = models.ForeignKey('mobs.MobRecord', null=True, default=None, blank=True)
    pref_mob_changed_at = models.DateTimeField(default=datetime.datetime(2000, 1, 1))

    pref_place = models.ForeignKey('places.Place', null=True, default=None, related_name='+', blank=True)
    pref_place_changed_at = models.DateTimeField(default=datetime.datetime(2000, 1, 1))

    pref_friend = models.ForeignKey('persons.Person', null=True, default=None, related_name='+', blank=True)
    pref_friend_changed_at = models.DateTimeField(default=datetime.datetime(2000, 1, 1))

    pref_enemy = models.ForeignKey('persons.Person', null=True, default=None, related_name='+', blank=True)
    pref_enemy_changed_at = models.DateTimeField(default=datetime.datetime(2000, 1, 1))

    pref_equipment_slot = models.CharField(max_length=16, null=True, default=None, blank=True)
    pref_equipment_slot_changed_at = models.DateTimeField(default=datetime.datetime(2000, 1, 1))

    #statistics
    stat_pve_deaths = models.BigIntegerField(default=0, null=False)
    stat_pve_kills = models.BigIntegerField(default=0, null=False)

    stat_money_earned_from_loot = models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_artifacts = models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_quests = models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_help = models.BigIntegerField(default=0, null=False)

    stat_money_spend_for_heal = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_artifacts = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_sharpening = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_useless = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_impact = models.BigIntegerField(default=0, null=False)

    stat_artifacts_had = models.BigIntegerField(default=0, null=False)
    stat_loot_had = models.BigIntegerField(default=0, null=False)

    stat_quests_done = models.BigIntegerField(default=0, null=False)

    stat_pvp_battles_1x1_number = models.BigIntegerField(default=0, null=False)
    stat_pvp_battles_1x1_victories = models.BigIntegerField(default=0, null=False)
    stat_pvp_battles_1x1_draws = models.BigIntegerField(default=0, null=False)

    def __unicode__(self):
        return u'hero[%d] - %s' % (self.id, self.name)
