useragent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.79 Safari/537.1 L_y_n_x/2.7"

if [ ! -f ./q ]
then
    wget -q https://raw.githubusercontent.com/harelba/q/1.7.1/bin/q
    chmod 755 ./q
fi

if [ -z "$(lynx -version 2>/dev/null)" ]
then
    echo "lynx not found"
    exit 1
fi

if [ -z "$(tidy -version 2>/dev/null)" ]
then
    echo "tidy not found"
    exit 1
fi

echo "$(date) - Investment Trusts"
echo "epic,sector_desc" >>./invtrust_sectors.csv
lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/investment-trusts" |sed -n '/<select id="sectorid" name="sectorid"*/,/<\/select>/p' |grep 'option value' |grep -v '<option value="">Please select</option>' |grep -v VCT |while read rec
do
    sector_id=$(echo $rec |cut -f2 -d'"')
    sector_desc=$(echo $rec |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/\&amp;/\&/g' |sed 's/Sector Specialist: //g')
    lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/investment-trusts/search-for-investment-trusts?companyid=&tab=prices&sectorid=${sector_id}&tab=prices&it_search_input=" |grep shares-search-results |cut -f6 -d"/" |cut -f1 -d'"' |sort |uniq |while read epic
    do
        echo "$epic,$sector_desc" >>./invtrust_sectors.csv
    done
done

echo "$(date) - Downloading Investment Trust Details"
rm -fR ./invtrusts
mkdir ./invtrusts
./q -H -d',' "select distinct epic from ./invtrust_sectors.csv" |while read epic
do
    lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/shares-search-results/$epic" |sed -n '/<table class="factsheet-table/,/<\/table>/p' |tidy >./invtrusts/${epic}.html 2>/dev/null &
    while [ $(pgrep -f lynx |wc -l) -gt 20 ]
    do
        sleep 1
    done
done
while [ $(pgrep -f lynx |wc -l) -gt 0 ]
do
   sleep 1
done

echo "$(date) - Generating ./invtrust_details.csv"
echo "epic,pd,pd12,charge" >./invtrust_details.csv
./q -H -d',' "select distinct epic from ./invtrust_sectors.csv" |while read rec
do
    epic=$(echo "$rec" |cut -f1 -d',')
    file=./invtrusts/${epic}.html
    charge=$(grep -A1 -i 'ongoing charge' $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    pd=$(egrep -A1 -i '^premium'  $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    pd12=$(egrep -A1 -i '^12m average premium'  $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    echo "$epic,$pd,$pd12,$charge" >>./invtrust_details.csv
done

./q -O -H -d',' "select es.sector_desc from ./invtrust_sectors.csv es join ./invtrust_details.csv id on es.epic = id.epic
  where es.epic in (select epic from ./invtrust_sectors.csv group by epic having count(*) = 1)
  and pd12 > -90 and pd12 < 100
  group by sector_desc having count(pd12) > 2 order by avg(pd12)" |head -7 >./unfashionable_sectors.csv



echo "$(date) - ETFs"
echo "epic,sector_desc" >./etf_sectors.csv
rm -f ./etf_sectors.tmp
lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/exchange-traded-funds-etfs" \
  |sed -n '/<option value="">Please select sector<\/option>/,/<\/select>/p' \
  |grep 'option value' |grep -v '<option value="">Please select sector</option>' |while read rec
do
    sector_id=$(echo $rec |cut -f2 -d'"')
    sector_desc=$(echo $rec |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/\&amp;/\&/g' |sed "s/^ //" |sed 's/,//g')
    seq 0 50 500 |while read offset
    do
        lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/exchange-traded-funds-etfs/list-of-etfs?offset=${offset}&etf_search_input=&companyid=&sectorid=${sector_id}&non_soph=1"  |grep shares-search-results |cut -f6 -d"/" |cut -f1 -d'"' |while read epic
        do
            echo "$epic,$sector_desc" >>./etf_sectors.tmp
        done
    done
done
cat ./etf_sectors.tmp |sort |uniq >>./etf_sectors.csv
rm -f ./etf_sectors.tmp

echo "$(date) - Downloading ETF Details"
rm -fR ./etfs
mkdir ./etfs
./q -H -d',' "select substr('0000000'||epic, -7, 7) from ./etf_sectors.csv group by epic having count(*) = 1" |while read epic
do
    lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/shares-search-results/$epic" |sed -n '/<table class="factsheet-table/,/<\/table>/p' |tidy >./etfs/${epic}.html 2>/dev/null &
    while [ $(pgrep -f lynx |wc -l) -gt 20 ]
    do
        sleep 1
    done
done
while [ $(pgrep -f lynx |wc -l) -gt 0 ]
do
   sleep 1
done

echo "$(date) - Finished"
exit 0

echo "epic,charge" >./etf_details.csv
for file in ./tmp/*
do
    epic=$(basename $file .html)
    charge=$(grep -A1 -i 'ongoing charge' $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    if [ "$charge" == ":" ]
    then
        charge=$(grep -A1 'Ongoing Charge (OCF/TER)' $file  |tail -1  |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    fi
    pd=$(egrep -A1 -i '^premium'  $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    pd12=$(egrep -A1 -i '^12m average premium'  $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    if [ -n "$charge" ]
    then
        echo "$epic,$pd,$pd12,$charge" >>./invtrust_details.csv
    else
        echo "No charge for http://www.hl.co.uk/shares/shares-search-results/$epic in $file"
    fi
done

rm -fR ./tmp/ ./sectors.csv

./q -O -H -d',' "select sector from ./invtrust_details.csv ed join ./sector_epics.csv se on ed.epic = se.epic
  where ed.epic in (select epic from ./sector_epics.csv group by epic having count(*) = 1)
  and pd12 > -90 and pd12 < 100
  group by sector having count(pd12) > 2 order by avg(pd12)" |head -7 >./unfashionable_sectors.csv

./q -H -d',' "select sector_desc from ./unfashionable_sectors.csv" |while read sector_desc
do
    echo
    echo "$sector_desc"
    echo "================================"
    echo
    ./q -O -H -d',' "select 'http://www.hl.co.uk/shares/shares-search-results/'||substr('0000000'||id.epic, -7, 7) url,pd discount,charge from ./invtrust_details.csv id
           join ./invtrust_sectors.csv isec on id.epic = isec.epic where isec.sector_desc = '$sector_desc' and charge < 2 order by charge,pd" |column -s ',' -t
done

echo "epic,gain" >./myepics.csv
if [ $(find ~/temp/myshares.html -mtime -1) ]
then
    tidy -w  ~/temp/myshares.html 2>/dev/null |sed -n '/<table id="holdings-table/,/<\/table>/p' |egrep 'link-headline|negative detail|positive detail' |grep -v gainpc |sed ':begin;$!N;s|\(<br />\)\n|\1|;tbegin;P;D' |while read rec
    do
      epic=$(echo $rec  |cut -f7 -d'/' |cut -f1 -d'"')
      gain=$(echo $rec  |cut -f9 -d'>' |cut -f1 -d'<')
      echo "$epic,$gain" >>./myepics.csv
    done
fi

./q -H -d',' "select me.epic, se.sector from ./myepics.csv me join ./sector_epics.csv se on me.epic = se.epic where gain > 12"
