# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.models import get_now
from openprocurement.api.tests.base import EncryptionTenderWebTest, test_tender_data, test_features_tender_data, test_organization, test_lots


class TenderBidEncryptionTest(EncryptionTenderWebTest):
    initial_status = 'active.tendering'
    initial_data = test_tender_data

    def test_encryption_create_tender_bid(self):
        # import pdb; pdb.set_trace()
        response = self.dryrun.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'tenderers': [test_organization], "value": {"amount": 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']
        separated_bid = response.json['parts']
        bid_status = bid.pop('status')
        self.assertEqual(set(bid) - set(separated_bid[u'active.qualification']), set(separated_bid['active.auction']))
        self.assertEqual(set(bid.keys()) - set(separated_bid[u'active.auction']), set(separated_bid['active.qualification']))
        bid['status'] = bid_status


class TenderBidFeaturesEncryptionTest(EncryptionTenderWebTest):
    initial_data = test_features_tender_data
    initial_status = 'active.tendering'

    def test_encryption_features_bid(self):
        bid = {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.15,
                }
                for i in self.initial_data['features']
            ],
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": 479,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            }
        }
        response = self.dryrun.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']
        separated_bid = response.json['parts']
        bid_status = bid.pop('status')
        self.assertEqual(set(bid) - set(separated_bid[u'active.qualification']), set(separated_bid['active.auction']))
        self.assertEqual(set(bid.keys()) - set(separated_bid[u'active.auction']), set(separated_bid['active.qualification']))
        bid['status'] = bid_status


class TenderLotBidEncryptionTest(EncryptionTenderWebTest):
    initial_status = 'active.tendering'
    initial_lots = test_lots

    def test_encryption_create_tender_bid(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        response = self.dryrun.post_json(request_path, {'data': {'tenderers': [test_organization], 'lotValues': [{"value": {"amount": 500}, 'relatedLot': self.initial_lots[0]['id']}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']
        separated_bid = response.json['parts']
        bid_status = bid.pop('status')
        self.assertEqual(set(bid) - set(separated_bid[u'active.qualification']), set(separated_bid['active.auction']))
        self.assertEqual(set(bid.keys()) - set(separated_bid[u'active.auction']), set(separated_bid['active.qualification']))
        bid['status'] = bid_status


class TenderLotFeatureBidEncryptionTest(EncryptionTenderWebTest):
    initial_lots = test_lots
    initial_data = test_features_tender_data

    def setUp(self):
        super(TenderLotFeatureBidEncryptionTest, self).setUp()
        self.lot_id = self.initial_lots[0]['id']
        tender = self.db[self.tender_id]
        tender['items'][0].update({'relatedLot': self.lot_id, 'id': '1'})
        tender.update({
            "features": [
                {
                    "code": "code_item",
                    "featureOf": "item",
                    "relatedItem": "1",
                    "title": u"item feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_lot",
                    "featureOf": "lot",
                    "relatedItem": self.lot_id,
                    "title": u"lot feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_tenderer",
                    "featureOf": "tenderer",
                    "title": u"tenderer feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                }
            ]
        })
        self.db.save(tender)
        self.set_status('active.tendering')

    def test_encryption_create_tender_bid(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        response = self.dryrun.post_json(request_path, {'data': {'tenderers': [test_organization], 'lotValues': [{"value": {"amount": 500}, 'relatedLot': self.lot_id}], 'parameters': [
            {"code": "code_item", "value": 0.01},
            {"code": "code_tenderer", "value": 0.01},
            {"code": "code_lot", "value": 0.01},
        ]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']
        separated_bid = response.json['parts']
        bid_status = bid.pop('status')
        self.assertEqual(set(bid) - set(separated_bid[u'active.qualification']), set(separated_bid['active.auction']))
        self.assertEqual(set(bid.keys()) - set(separated_bid[u'active.auction']), set(separated_bid['active.qualification']))
        bid['status'] = bid_status


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderEncryptionTest))
    suite.addTest(unittest.makeSuite(TenderBidEncryptionTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesEncryptionTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
