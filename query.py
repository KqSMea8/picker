#!/usr/bin/env python3
import sqlite3

db = sqlite3.connect('invtrusts.db')
c_unf_sector = db.cursor()
c_sectors = db.cursor()
c_inv_detail = db.cursor()


for unf_sector_row in c_unf_sector.execute('select iss.sector_desc from inv_search_sectors iss ' +
  'join inv_details id on iss.inv_id = id.inv_id ' +
  'where pd12 > -90 and pd12 < 100 ' +
  'group by iss.sector_desc having count(*) > 2 ' +
  'order by avg(pd12) limit 5'):
    unf_sector_desc = unf_sector_row[0]
    for inv_detail in c_sectors.execute('select inv_url, inv_desc, charge, pd from inv_details where inv_id in (select inv_id from inv_search_sectors where sector_desc = ?) and charge < 2 order by charge, pd', (unf_sector_desc,)):
        print("|[%s](%s \"Link\")|%s|%s|\n" % (inv_detail[1], inv_detail[0], inv_detail[2], inv_detail[3]))
