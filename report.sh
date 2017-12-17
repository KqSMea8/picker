
./q -O -H -d',' "select es.sector_desc, avg(pd12) avg from ./invtrust_sectors.csv es
  join ./invtrust_details.csv id on es.epic = id.epic
  where pd12 > -90 and pd12 < 100
  group by es.sector_desc having count(*) > 2" >./unfashionable_sectors.csv

./q -H -d',' "select isec.sector_desc from ./invtrust_sectors.csv isec
  join ./unfashionable_sectors.csv us on (isec.sector_desc = us.sector_desc)
  join ./invtrust_details.csv id on (isec.epic = id.epic)
  where id.charge < 2
  group by isec.sector_desc order by us.avg" |head -7 |while read sector_desc
do
    echo
    echo "$sector_desc"
    echo "================================"
    echo
    ./q -O -H -d',' "select distinct 'http://www.hl.co.uk/shares/shares-search-results/'||substr('0000000'||id.epic, -7, 7) url,pd discount,charge from ./invtrust_details.csv id
           join ./invtrust_sectors.csv isec on id.epic = isec.epic where isec.sector_desc = '$sector_desc' and charge < 2 order by charge,pd" |column -s ',' -t
done

echo
echo "ETFs"
echo "================================"
echo
./q -O -H -d',' "select 'http://www.hl.co.uk/shares/shares-search-results/'||substr('0000000'||ed.epic, -7, 7) url, es.sector_desc, ed.charge from ./etf_details.csv ed join ./etf_sectors.csv es on (ed.epic = es .epic) order by charge" |head -50 |column -s ',' -t
