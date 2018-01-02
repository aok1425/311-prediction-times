# This is the canonical location for outliers for the whole repo

BLOCK_GROUP_BLACKLIST = ["9807001", "9818001", "0303003", "0701018", "9811003"] # these are parks or South Station
OUTLIERS_COMMERCIAL_INDUSTRIAL = ['0102034', '0107013', '0512001', '0612002', '0701012', '1101033', '9812021']
OUTLIERS_LOW_POP = ['0005024', '0008032', '0103002', '0104051'] # cemeteries, by Arboretum
OUTLIERS_POP_0 = [u'9811002', u'9815011', u'9810001', u'9811001', u'9816001', u'9817001', u'9812011', u'9815021']

outliers = BLOCK_GROUP_BLACKLIST + OUTLIERS_POP_0 + OUTLIERS_LOW_POP + OUTLIERS_COMMERCIAL_INDUSTRIAL