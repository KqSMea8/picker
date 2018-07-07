./q -O -H -d '|' "select url, name, market_cap,
round(total_liabilities1/(total_assets1 - total_liabilities1), 2) debt_ratio,
round(current_assets/current_liabilities, 2) current_ratio,
round(net_income1/(total_assets1 - total_liabilities1), 2) roe1,
round(net_income2/(total_assets2 - total_liabilities2), 2) roe2,
round(net_income3/(total_assets3 - total_liabilities3), 2) roe3,
round(net_income4/(total_assets4 - total_liabilities4), 2) roe4,
round(net_income5/(total_assets5 - total_liabilities5), 2) roe5,
pe_ratio,
round(price/((equity*1000000)/volume), 2) pb_ratio
from ./stock_details.csv where
debt_ratio < 0.5
and current_ratio > 1.5
and roe1 > 0.08
and roe2 > 0.08
and roe3 > 0.08
and roe4 > 0.08
and roe5 > 0.08
and pe_ratio < 15
and pe_ratio_prev < 15
and pb_ratio < 1.5
order by debt_ratio, pe_ratio asc" >./stock_picks.csv


echo " "
echo "# Stock Picks"
echo "| Stock | Market Cap | Debt Ratio | ROE | P/E | P/B |"
echo "| ----- | ---------- | ----------:| ---:| ---:| ---:|"
./q -H -d '|' "select url, name, market_cap, debt_ratio, roe1, pe_ratio, pb_ratio from ./stock_picks.csv" |while read rec
do
    url=$(echo $rec |cut -f1 -d'|')
    name=$(echo $rec |cut -f2 -d'|')
    market_cap=$(echo $rec |cut -f3 -d'|')
    debt_ratio=$(echo $rec |cut -f4 -d'|')
    roe=$(echo $rec |cut -f5 -d'|')
    pe=$(echo $rec |cut -f6 -d'|')
    pb=$(echo $rec |cut -f7 -d'|')
    echo "[${name}](${url} \"URL\")|${market_cap}|${debt_ratio}|${roe}|${pe}|${pb}|"
done


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


# echo "# ETFs"
# echo "| ETF | Sector | Charge | Spread |"
# echo "| --- | ------ | ------:| ------:|"
# echo "desc,sector,charge,spread" >./etfs.csv
#  ./q -H -d',' "select substr('0000000'||ed.epic, -7, 7) url, ed.desc, es.sector_desc, ed.charge||'%', ed.spread||'%' from ./etf_details.csv ed \
#  join ./etf_sectors.csv es on (ed.epic = es.epic) \
#  join ./etf_sectors_shortlist.csv ess on (es.sector_desc = ess.sector_desc) \
#  order by es.sector_desc,charge,spread" |while read rec
# do
#    link="http://www.hl.co.uk/shares/shares-search-results/$(echo $rec |cut -f1 -d',')"
#    desc=$(echo $rec |cut -f2 -d',' |sed 's/|/-/g')
#    sector=$(echo $rec |cut -f3 -d',' |cut -f2 -d'-')
#    charge=$(echo $rec |cut -f4 -d',')
#    spread=$(echo $rec |cut -f5 -d',')
#   echo "|[${desc}](${link} \"${desc}\")|${sector}|${charge}|${spread}|"
#   echo "${desc},${sector},${charge},${spread}" >>./etfs.csv
# done
