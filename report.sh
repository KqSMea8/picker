
./q -O -H -d',' "select es.sector_desc, avg(pd12) avg from ./invtrust_sectors.csv es
  join ./invtrust_details.csv id on es.epic = id.epic
  where pd12 > -90 and pd12 < 100
  group by es.sector_desc having count(*) > 2" >./unfashionable_sectors.csv


echo "<!DOCTYPE html>
<html>
<head>
<style>
#mytable {
    font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
    border-collapse: collapse;
    width: 50%;
}

#mytable td, #mytable th {
    border: 1px solid #ddd;
    padding: 8px;
}

#mytable tr:nth-child(even){background-color: #f2f2f2;}

#mytable tr:hover {background-color: #ddd;}

#mytable th {
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: #4CAF50;
    color: white;
}
</style>
</head>
<body>"
./q -H -d',' "select isec.sector_desc from ./invtrust_sectors.csv isec
  join ./unfashionable_sectors.csv us on (isec.sector_desc = us.sector_desc)
  join ./invtrust_details.csv id on (isec.epic = id.epic)
  where id.charge < 2
  group by isec.sector_desc order by us.avg" |head -7 |while read sector_desc
do
    echo "<h1>$sector_desc</h1>
<table id=\"mytable\">
  <tr>
    <th>URL</th>
    <th>Discount</th>
    <th>Charge</th>
  </tr>
"
    ./q -H -d',' "select distinct substr('0000000'||id.epic, -7, 7),pd discount,charge from ./invtrust_details.csv id
           join ./invtrust_sectors.csv isec on id.epic = isec.epic where isec.sector_desc = '$sector_desc' and charge < 2 order by charge,pd" |while read rec
       do
           link="http://www.hl.co.uk/shares/shares-search-results/$(echo $rec |cut -f1 -d',')"
           discount=$(echo $rec |cut -f2 -d',')
           charge=$(echo $rec |cut -f3 -d',')
           echo "<p><tr><td><a href=\"${link}\">Link</a></td><td>${discount}</td><td>${charge}</td></tr></p>"
       done
    echo "</table>"
done

echo "<h1>ETFs</h1>
<table id=\"mytable\">
  <tr>
    <th>URL</th>
    <th>Sector</th>
    <th>Charge</th>
  </tr>
"
 ./q -H -d',' "select substr('0000000'||ed.epic, -7, 7) url, es.sector_desc, ed.charge from ./etf_details.csv ed join ./etf_sectors.csv es on (ed.epic = es .epic) order by charge" |while read rec
do
   link="http://www.hl.co.uk/shares/shares-search-results/$(echo $rec |cut -f1 -d',')"
   sector=$(echo $rec |cut -f2 -d',')
   charge=$(echo $rec |cut -f3 -d',')
   echo "<p><tr><td><a href=\"${link}\">Link</a></td><td>${sector}</td><td>${charge}</td></tr></p>"
done
echo "</body>
</html>
"
