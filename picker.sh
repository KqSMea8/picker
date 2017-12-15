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

mkdir -p ./tables
rm -f ./tables/*
echo "$(date) - Investment Trusts  >./tables/sector_epics.csv"
echo "sector,epic" >./tables/sector_epics.csv
lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/investment-trusts" |sed -n '/<select id="sectorid" name="sectorid"*/,/<\/select>/p' |grep 'option value' |grep -v '<option value="">Please select</option>' |grep -v VCT |sort |while read rec
do
    sector_id=$(echo $rec |cut -f2 -d'"')
    sector=$(echo $rec |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/\&amp;/\&/g' |sed 's/Sector Specialist: //g')
    lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/investment-trusts/search-for-investment-trusts?companyid=&tab=prices&sectorid=${sector_id}&tab=prices&it_search_input=" |grep shares-search-results |cut -f6 -d"/" |cut -f1 -d'"' |sort |uniq |while read epic
    do
        echo "$sector,$epic" >>./tables/sector_epics.csv
    done
done

echo "$(date) - ETFs  >./sector_epics.csv"
rm -f ./sort.tmp ./etfs.tmp
lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/exchange-traded-funds-etfs" |sed -n '/<option value="">Please select sector<\/option>/,/<\/select>/p' |grep 'option value' |grep -v '<option value="">Please select sector</option>' |sort |egrep 'Commodity|Equity' |while read rec
do
    sector_id=$(echo $rec |cut -f2 -d'"')
    sector=$(echo $rec |cut -f2 -d'>' |cut -f1 -d'<' |cut -f2 -d'-' |sed 's/\&amp;/\&/g' |sed 's/Banks \& //g' |sed 's/& South //g' |sed "s/^ //")
    it_sector=$(grep "$sector" ./tables/unfashionable_sectors.csv |head -1 |cut -f1 -d',')
    if [ -n "$it_sector" ]
    then
        seq 0 50 500 |while read offset
        do
          lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/exchange-traded-funds-etfs/list-of-etfs?offset=${offset}&etf_search_input=&companyid=&sectorid=${sector_id}&non_soph=1"  |grep shares-search-results |cut -f6 -d"/" |cut -f1 -d'"' |while read epic
            do
                echo "$sector,$epic" >>./sort.tmp
            done
        done
        echo "sector: $it_sector sort.tmp: $(wc -l ./sort.tmp)"
        sort ./sort.tmp |uniq >>./tables/sector_epics.csv
        cat ./sort.tmp |cut -f2 -d',' >>./etfs.tmp
    fi
    rm -f ./sort.tmp
done



echo "$(date) - Downloading details"
rm -fR ./tmp
mkdir ./tmp
./q -H -d',' "select epic from ./tables/sector_epics.csv" |while read epic
do
    lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/shares-search-results/$epic" |sed -n '/<table class="factsheet-table/,/<\/table>/p' |tidy >./tmp/${epic}.html 2>/dev/null &
    while [ $(pgrep -f lynx |wc -l) -gt 20 ]
    do
        sleep 1
    done
done
while [ $(pgrep -f lynx |wc -l) -gt 0 ]
do
   sleep 1
done

echo "$(date) - Generating ./tables/epic_details.csv"
echo "epic,pd,pd12,charge" >./tables/epic_details.csv
for file in ./tmp/*
do
    epic=$(basename $file .html)
    charge=$(grep -A1 -i 'ongoing charge' $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    pd=$(egrep -A1 -i '^premium'  $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    pd12=$(egrep -A1 -i '^12m average premium'  $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    # if [ -n "$charge" ]
    # then
        echo "$epic,$pd,$pd12,$charge" >>./tables/epic_details.csv
    # else
    #     echo "No charge for http://www.hl.co.uk/shares/shares-search-results/$epic in $file"
    # fi
done
rm -fR ./tmp/

./q -O -H -d',' "select sector from ./tables/epic_details.csv ed join ./tables/sector_epics.csv se on ed.epic = se.epic
  where ed.epic in (select epic from ./tables/sector_epics.csv group by epic having count(*) = 1)
  and pd12 > -90 and pd12 < 100
  group by sector having count(pd12) > 2 order by avg(pd12)" |head -7 >./tables/unfashionable_sectors.csv


exit 0



echo "$(date) - Downloading details"
rm -fR ./tmp
mkdir ./tmp
./q -H -d',' "select epic from ./sector_epics.csv" |while read epic
do
    lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/shares-search-results/$epic" |sed -n '/<table class="factsheet-table/,/<\/table>/p' |tidy >./tmp/${epic}.html 2>/dev/null &
    while [ $(pgrep -f lynx |wc -l) -gt 20 ]
    do
        sleep 1
    done
done
while [ $(pgrep -f lynx |wc -l) -gt 0 ]
do
   sleep 1
done

echo "epic,pd,pd12,charge" >./epic_details.csv
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
        echo "$epic,$pd,$pd12,$charge" >>./epic_details.csv
    else
        echo "No charge for http://www.hl.co.uk/shares/shares-search-results/$epic in $file"
    fi
done

rm -fR ./tmp/ ./sectors.csv

./q -O -H -d',' "select sector from ./epic_details.csv ed join ./sector_epics.csv se on ed.epic = se.epic
  where ed.epic in (select epic from ./sector_epics.csv group by epic having count(*) = 1)
  and pd12 > -90 and pd12 < 100
  group by sector having count(pd12) > 2 order by avg(pd12)" |head -7 >./unfashionable_sectors.csv

./q -H -d',' "select sector from ./unfashionable_sectors.csv" |while read sector
do
    echo
    echo "$sector"
    echo "================================"
    echo
    ./q -O -H -d',' "select 'http://www.hl.co.uk/shares/shares-search-results/'||substr('0000000'||ed.epic, -7, 7) url,pd discount,charge from ./epic_details.csv ed join ./sector_epics.csv se on ed.epic = se.epic where se.sector = '$sector' and charge < 2 order by charge,pd" |column -s ',' -t
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
