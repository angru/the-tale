# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Invoice.description_for_recipient'
        db.add_column(u'bank_invoice', 'description_for_recipient',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Invoice.description_for_sender'
        db.add_column(u'bank_invoice', 'description_for_sender',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding index on 'Invoice', fields ['recipient_type', 'recipient_id', 'currency']
        db.create_index(u'bank_invoice', ['recipient_type', 'recipient_id', 'currency'])

        # Adding index on 'Invoice', fields ['sender_type', 'sender_id', 'currency']
        db.create_index(u'bank_invoice', ['sender_type', 'sender_id', 'currency'])


    def backwards(self, orm):
        # Removing index on 'Invoice', fields ['sender_type', 'sender_id', 'currency']
        db.delete_index(u'bank_invoice', ['sender_type', 'sender_id', 'currency'])

        # Removing index on 'Invoice', fields ['recipient_type', 'recipient_id', 'currency']
        db.delete_index(u'bank_invoice', ['recipient_type', 'recipient_id', 'currency'])

        # Deleting field 'Invoice.description_for_recipient'
        db.delete_column(u'bank_invoice', 'description_for_recipient')

        # Deleting field 'Invoice.description_for_sender'
        db.delete_column(u'bank_invoice', 'description_for_sender')


    models = {
        u'bank.account': {
            'Meta': {'unique_together': "(('entity_id', 'entity_type', 'currency'),)", 'object_name': 'Account'},
            'amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'entity_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'entity_type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'bank.invoice': {
            'Meta': {'object_name': 'Invoice', 'index_together': "(('recipient_type', 'recipient_id', 'currency'), ('sender_type', 'sender_id', 'currency'))"},
            'amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'description_for_recipient': ('django.db.models.fields.TextField', [], {}),
            'description_for_sender': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation_uid': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'recipient_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'recipient_type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'sender_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'sender_type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['bank']