useragent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.79 Safari/537.1 L_y_n_x/2.7"
tempdir=/tmp/hldownload
cd $(dirname $0)

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

rm -fR $tempdir
mkdir -p $tempdir

echo "$(date) - Generating ./invtrust_sectors.csv"
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
./q -H -d',' "select distinct epic from ./invtrust_sectors.csv order by epic" |while read epic
do
    lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/shares-search-results/$epic" |sed -n '/<table class="factsheet-table/,/<\/table>/p' |tidy >$tempdir/${epic}.html 2>/dev/null &
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
./q -H -d',' "select distinct epic from ./invtrust_sectors.csv order by epic" |while read rec
do
    epic=$(echo "$rec" |cut -f1 -d',')
    file=$tempdir/${epic}.html
    charge=$(grep -A1 -i 'ongoing charge' $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    pd=$(egrep -A1 -i '^premium'  $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    pd12=$(egrep -A1 -i '^12m average premium'  $file |tail -1 |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    echo "$epic,$pd,$pd12,$charge" >>./invtrust_details.csv
done

echo "$(date) - Generating ./etf_sectors.csv"
echo "epic,sector_desc" >./etf_sectors.csv
lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/exchange-traded-funds-etfs" \
  |sed -n '/<option value="">Please select sector<\/option>/,/<\/select>/p' \
  |grep 'option value' |egrep "Commodity|Equity" |grep -v '<option value="">Please select sector</option>' |while read rec
do
    sector_id=$(echo $rec |cut -f2 -d'"')
    sector_desc=$(echo $rec |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/\&amp;/\&/g' |sed "s/^ //" |sed 's/,//g')
    lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/exchange-traded-funds-etfs/list-of-etfs?&etf_search_input=&companyid=&sectorid=${sector_id}&non_soph=1" >$tempdir/${sector_id}.tmp
    grep shares-search-results $tempdir/${sector_id}.tmp |cut -f6 -d"/" |cut -f1 -d'"' |while read epic
    do
        echo "$epic,$sector_desc" >>$tempdir/etf_sectors.tmp
    done

    grep offset $tempdir/${sector_id}.tmp |cut -f3 -d'=' |cut -f1 -d'&' |sort -n |uniq |while read offset
    do
        lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/exchange-traded-funds-etfs/list-of-etfs?offset=${offset}&etf_search_input=&companyid=&sectorid=${sector_id}&non_soph=1" \
        |grep shares-search-results |cut -f6 -d"/" |cut -f1 -d'"' \
        |while read epic
        do
            echo "$epic,$sector_desc" >>$tempdir/etf_sectors.tmp
        done
    done
done
cat $tempdir/etf_sectors.tmp |sort |uniq >>./etf_sectors.csv

echo "$(date) - Downloading ETF Details"
./q -H -d',' "select substr('0000000'||epic, -7, 7) from ./etf_sectors.csv group by epic having count(*) = 1 order by substr('0000000'||epic, -7, 7)" |while read epic
do
    lynx -source -useragent="$useragent" "http://www.hl.co.uk/shares/shares-search-results/$epic" |sed -n '/<table class="factsheet-table/,/<\/table>/p' |tidy >$tempdir/${epic}.html 2>/dev/null &
    while [ $(pgrep -f lynx |wc -l) -gt 20 ]
    do
        sleep 1
    done
done
while [ $(pgrep -f lynx |wc -l) -gt 0 ]
do
   sleep 1
done

echo "$(date) - Generating ./etf_details.csv"
echo "epic,charge" >./etf_details.csv
./q -H -d',' "select substr('0000000'||epic, -7, 7) from ./etf_sectors.csv group by epic having count(*) = 1 order by substr('0000000'||epic, -7, 7)" |while read epic
do
    file=$tempdir/${epic}.html
    charge=$(grep -A1 'Ongoing Charge (OCF/TER)' $file  |tail -1  |cut -f2 -d'>' |cut -f1 -d'<' |sed 's/n\/a//g' |sed 's/%//g')
    if [ -n "$charge" ]
    then
        echo "$epic,$charge" >>./etf_details.csv
    fi
done

rm -fR $tempdir/
echo
./report.sh >./report.txt
echo "$(date) - Finished"
git add --all >/dev/null
git commit -a -m "Crontab" >/dev/null
git push >/dev/null
