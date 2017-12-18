
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
    echo "# $sector_desc"
    ./q -H -d',' "select distinct substr('0000000'||id.epic, -7, 7),pd discount,charge from ./invtrust_details.csv id
           join ./invtrust_sectors.csv isec on id.epic = isec.epic where isec.sector_desc = '$sector_desc' and charge < 2 order by charge,pd" |while read rec
       do
           link="http://www.hl.co.uk/shares/shares-search-results/$(echo $rec |cut -f1 -d',')"
           discount=$(echo $rec |cut -f2 -d',')
           charge=$(echo $rec |cut -f3 -d',')
           echo "|[Link](${link} \"Link\")|${discount}|${charge}|"
       done
done

echo "# ETFs"
 ./q -H -d',' "select substr('0000000'||ed.epic, -7, 7) url, es.sector_desc, ed.charge from ./etf_details.csv ed join ./etf_sectors.csv es on (ed.epic = es .epic) order by charge" |while read rec
do
   link="http://www.hl.co.uk/shares/shares-search-results/$(echo $rec |cut -f1 -d',')"
   sector=$(echo $rec |cut -f2 -d',')
   charge=$(echo $rec |cut -f3 -d',')
  echo "|[Link](${link} \"Link\")|${sector}|${charge}|"
done
