from __future__ import absolute_import

import decimal

from django.test import TestCase
from django.utils import six

from .models import DecimalTable, PreciseDecimalTable

class GoogleBug85TestCase(TestCase):
    def test_european_decimal_conversion(self):
        from sqlserver_ado.dbapi import _cvtDecimal
        val1 = _cvtDecimal('0,05')
        self.assertEqual(decimal.Decimal('0.05'), val1)

    def test_european_float_conversion(self):
        from sqlserver_ado.dbapi import _cvtFloat
        val1 = _cvtFloat('0,05')
        self.assertEqual(float('0.05'), val1)


class GoogleBug38TestCase(TestCase):
    def testInsertVariousFormats(self):
        """
        Test adding decimals as strings with various formats.
        """
        DecimalTable(d=decimal.Decimal('0')).save()
        DecimalTable(d=decimal.Decimal('0e0')).save()
        DecimalTable(d=decimal.Decimal('0E0')).save()
        DecimalTable(d=decimal.Decimal('450')).save()
        DecimalTable(d=decimal.Decimal('450.0')).save()
        DecimalTable(d=decimal.Decimal('450.00')).save()
        DecimalTable(d=decimal.Decimal('450.000')).save()
        DecimalTable(d=decimal.Decimal('0450')).save()
        DecimalTable(d=decimal.Decimal('0450.0')).save()
        DecimalTable(d=decimal.Decimal('0450.00')).save()
        DecimalTable(d=decimal.Decimal('0450.000')).save()
        DecimalTable(d=decimal.Decimal('4.5e+2')).save()
        DecimalTable(d=decimal.Decimal('4.5E+2')).save()
        self.assertEquals(len(list(DecimalTable.objects.all())),13)

    def testReturnsDecimal(self):
        """
        Test if return value is a python Decimal object
        when saving the model with a Decimal object as value
        """
        DecimalTable(d=decimal.Decimal('0')).save()
        d1 = DecimalTable.objects.all()[0]
        self.assertEquals(decimal.Decimal, d1.d.__class__)

    def testReturnsDecimalFromString(self):
        """
        Test if return value is a python Decimal object
        when saving the model with a unicode object as value.
        """
        DecimalTable(d=six.text_type('123')).save()
        d1 = DecimalTable.objects.all()[0]
        self.assertEquals(decimal.Decimal, d1.d.__class__)

    def testSavesAfterDecimal(self):
        """
        Test if value is saved correctly when there are numbers
        to the right side of the decimal point
        """
        DecimalTable(d=decimal.Decimal('450.1')).save()
        d1 = DecimalTable.objects.all()[0]
        self.assertEquals(decimal.Decimal('450.1'), d1.d)

    def testInsertWithMoreDecimals(self):
        """
        Test if numbers to the right side of the decimal point
        are saved correctly rounding to a decimal with the correct
        decimal places.
        """
        DecimalTable(d=decimal.Decimal('450.111')).save()
        d1 = DecimalTable.objects.all()[0]
        self.assertEquals(decimal.Decimal('450.11'), d1.d)

    def testInsertWithLeadingZero(self):
        """
        Test if value is saved correctly with Decimals with a leading zero.
        """
        DecimalTable(d=decimal.Decimal('0450.0')).save()
        d1 = DecimalTable.objects.all()[0]
        self.assertEquals(decimal.Decimal('450.0'), d1.d)

class DecimalRegressTestCase(TestCase):
    def test_very_precise_decimal(self):
        """
        Issue #50 - decimals are rounded to 4 places by ADO
        """
        expected = decimal.Decimal('1234567890.0123456789')
        PreciseDecimalTable(d=expected).save()
        self.assertEquals(expected, PreciseDecimalTable.objects.all()[0].d)

    def test_positive_exp(self):
        """
        Issue #55 - Decimals like '2.82E+3' fail.
        """
        expected = decimal.Decimal('28.2') / decimal.Decimal('0.01')
        PreciseDecimalTable(d=expected).save()
        self.assertEquals(expected, PreciseDecimalTable.objects.all()[0].d)
