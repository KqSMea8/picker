
./q -O -H -d',' "select es.sector_desc, avg(pd12) avg from ./invtrust_sectors.csv es
  join ./invtrust_details.csv id on es.epic = id.epic
  where pd12 > -90 and pd12 < 100
  group by es.sector_desc having count(*) > 2" >./unfashionable_sectors.csv


./q -H -d',' "select isec.sector_desc from ./invtrust_sectors.csv isec
  join ./unfashionable_sectors.csv us on (isec.sector_desc = us.sector_desc)
  join ./invtrust_details.csv id on (isec.epic = id.epic)
  where id.charge < 2
  group by isec.sector_desc order by us.avg" |head -6 |while read sector_desc
do
    num=$(./q -H -d',' "select count(*) from ./invtrust_details.csv id
           join ./invtrust_sectors.csv isec on id.epic = isec.epic \
           where isec.sector_desc = '$sector_desc' and pd < -1 and charge < 2 and spread < 5")
    if [ $num -gt 0 ]
    then
        echo "# $sector_desc"
        echo "| Investment Trust | Discount | Charge | Spread |"
        echo "| ---------------- | --------:| ------:| ------:|"
        ./q -H -d',' "select distinct substr('0000000'||id.epic, -7, 7) url,id.desc,pd||'%' discount,charge||'%', spread||'%' from ./invtrust_details.csv id
               join ./invtrust_sectors.csv isec on id.epic = isec.epic \
               where isec.sector_desc = '$sector_desc' and pd < -1 and charge < 2 and spread < 5 order by charge,pd,spread" |while read rec
           do
               link="http://www.hl.co.uk/shares/shares-search-results/$(echo $rec |cut -f1 -d',')"
               desc=$(echo $rec |cut -f2 -d',' |sed 's/|/-/g')
               discount=$(echo $rec |cut -f3 -d',')
               charge=$(echo $rec |cut -f4 -d',')
               spread=$(echo $rec |cut -f5 -d',')
               echo "|[${desc}](${link} \"Link\")|${discount}|${charge}|${spread}|"
           done
     fi
done

echo "# ETFs"
echo "| ETF | Sector | Charge | Spread |"
echo "| --- | ------ | ------:| ------:|"
echo "desc,sector,charge,spread" >./etfs.csv
 ./q -H -d',' "select substr('0000000'||ed.epic, -7, 7) url, ed.desc, es.sector_desc, ed.charge||'%', ed.spread||'%' from ./etf_details.csv ed \
 join ./etf_sectors.csv es on (ed.epic = es.epic) \
 join ./etf_sectors_shortlist.csv ess on (es.sector_desc = ess.sector_desc) \
 order by es.sector_desc,charge,spread" |while read rec
do
   link="http://www.hl.co.uk/shares/shares-search-results/$(echo $rec |cut -f1 -d',')"
   desc=$(echo $rec |cut -f2 -d',' |sed 's/|/-/g')
   sector=$(echo $rec |cut -f3 -d',' |cut -f2 -d'-')
   charge=$(echo $rec |cut -f4 -d',')
   spread=$(echo $rec |cut -f5 -d',')
  echo "|[${desc}](${link} \"${desc}\")|${sector}|${charge}|${spread}|"
  echo "${desc},${sector},${charge},${spread}" >>./etfs.csv
done
