tempdir=/tmp/hldata

tonum()
{
	declare input=${1:-$(</dev/stdin)};
	echo "$input" |cut -f2 -d':' |sed 's/(/-/g' |tr -d 'abcdefghijklmnopqrstuvwxyz/,)'
}


echo "$(date) - Generating ./stock_details.csv"
echo "url|name|market_cap|price|pe_ratio|volume|equity|net_income1|total_assets1|total_liabilities1|net_income2|total_assets2|total_liabilities2|net_income3|total_assets3|total_liabilities3|net_income4|total_assets4|total_liabilities4|net_income5|total_assets5|total_liabilities5|current_assets|current_liabilities" >./stock_details.csv
ls $tempdir/stocks/*.url |while read urlfile
do
    dir=$(dirname $urlfile)
    head=$dir/$(basename $urlfile .url).head
    detl=$dir/$(basename $urlfile .url).detl
    url="$(cat $urlfile)"
    if [ -s "$head" -a -s "$detl" -a -z "$(grep 'it cannot be purchased' $head)" ]
    then
        name=$(head -3 $head |tail -1)
        market_cap=$(grep 'Market capitalisation:Market cap.:' $head |sed 's/ //g' |cut -f3 -d:)
        if [ -z "$market_cap" ]
        then
            market_cap=$(grep -A 3 'Market capitalisation' $head |tail -1 |xargs)
        fi
        price=$(grep Buy $head |tail -1 |cut -f2 -d:)
        pe_ratio=$(grep -A 1 'P/E ratio:' $head |tail -1 |xargs)
        if [ -z "$pe_ratio" ]
        then
            pe_ratio=$(grep 'P/E ratio' $head |tail -1 |awk '{ print $3 }' |sed 's|n/a||g')
        fi
        volume=$(grep -A 1 'Volume:' $head |tail -1 |xargs |sed 's|n/a||g' |sed 's/,//g')
        equity=$(grep 'Total Equity:' $detl |tonum |awk '{ print $1 }')
        net_income1=$(grep 'Profit after tax from continuing operations:' $detl |tonum |awk '{ print $1 }')
        total_assets1=$(grep 'Total Assets:' $detl |tonum |awk '{ print $1 }')
        total_liabilities1=$(grep 'Total Liabilities:' $detl |tonum |awk '{ print $1 }')
        net_income2=$(grep 'Profit after tax from continuing operations:' $detl |tonum |awk '{ print $2 }')
        total_assets2=$(grep 'Total Assets:' $detl |tonum |awk '{ print $2 }')
        total_liabilities2=$(grep 'Total Liabilities:' $detl |tonum |awk '{ print $2 }')
        net_income3=$(grep 'Profit after tax from continuing operations:' $detl |tonum |awk '{ print $3 }')
        total_assets3=$(grep 'Total Assets:' $detl |tonum |awk '{ print $3 }')
        total_liabilities3=$(grep 'Total Liabilities:' $detl |tonum |awk '{ print $3 }')
        net_income4=$(grep 'Profit after tax from continuing operations:' $detl |tonum |awk '{ print $4 }')
        total_assets4=$(grep 'Total Assets:' $detl |tonum |awk '{ print $4 }')
        total_liabilities4=$(grep 'Total Liabilities:' $detl |tonum |awk '{ print $4 }')
        net_income5=$(grep 'Profit after tax from continuing operations:' $detl |tonum |awk '{ print $5 }')
        total_assets5=$(grep 'Total Assets:' $detl |tonum |awk '{ print $5 }')
        total_liabilities5=$(grep 'Total Liabilities:' $detl |tonum |awk '{ print $5 }')
        current_assets=$(grep -A 1 'Other Current Assets:' $detl |tail -1 |tonum |awk '{ print $1 }')
        current_liabilities=$(grep -A 1 'Other Current Liabilities:' $detl |tail -1 |tonum |awk '{ print $1 }')
        if [ -n "${total_assets1}" ]
        then
            echo "${url}|${name}|${market_cap}|${price}|${pe_ratio}|${volume}|${equity}|${net_income1}|${total_assets1}|${total_liabilities1}|${net_income2}|${total_assets2}|${total_liabilities2}|${net_income3}|${total_assets3}|${total_liabilities3}|${net_income4}|${total_assets4}|${total_liabilities4}|${net_income5}|${total_assets5}|${total_liabilities5}|${current_assets}|${current_liabilities}" >>./stock_details.csv
        fi
    fi
done
