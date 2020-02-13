sed -i 's/_sources/sources/g' build/html/*html
sed -i 's/_modules/modules/g' build/html/*html
sed -i 's/_static/static/g' build/html/*html

mv build/html/_static build/html/static
mv build/html/_modules build/html/modules
mv build/html/_sources build/html/sources
