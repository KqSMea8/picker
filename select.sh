col=$1
sel="select url, $col from ./stock_details.csv"
./q -O -H -d '|' -T "$sel"
# echo " "
# ./q -O -H -d ',' "$sel" |tail -5
